import copy
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from filuta_fastapi_users import models
from filuta_fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from filuta_fastapi_users.authentication.mfa.otp_manager import OtpManager, OtpManagerDependency
from filuta_fastapi_users.manager import BaseUserManager, UserManagerDependency


class OtpResponse(BaseModel):
    status: bool
    message: str | None
    error: str | None
    access_token: Any | None


def get_otp_router(  # noqa: C901
    backend: AuthenticationBackend[models.UP, models.ID, models.AP],
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator[models.UP, models.ID, models.AP],
    get_otp_manager: OtpManagerDependency[models.OTPTP],
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()

    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification, authorized=False
    )

    get_current_active_user = authenticator.current_user(active=True, verified=requires_verification, authorized=False)

    class ValidateObtainOtpTokenRequestBody(BaseModel):
        type: str

    @router.post(
        "/otp/send-token",
        response_model=OtpResponse,
        name=f"auth:{backend.name}.send_otp_token",
        dependencies=[Depends(get_current_active_user)],
    )
    async def send_otp_token(
        request: Request,
        jsonBody: ValidateObtainOtpTokenRequestBody,
        user_token: tuple[models.UP, str] = Depends(get_current_user_token),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        otp_manager: OtpManager[models.OTPTP] = Depends(get_otp_manager),
        strategy: Strategy[models.UP, models.ID, models.AP] = Depends(backend.get_strategy),
    ) -> OtpResponse:
        user, token = user_token
        target_mfa_verification = jsonBody.type

        access_token_record = await strategy.get_token_record(token=token)
        if access_token_record is not None:
            token_mfas = access_token_record.mfa_scopes

        if "email" in token_mfas and target_mfa_verification == "email":
            already_obtained = await otp_manager.user_has_issued_token(token, target_mfa_verification)
            otp_token = otp_manager.generate_otp_token()

            if already_obtained is not None:
                await otp_manager.delete_record(already_obtained)

            otp_token_record = await otp_manager.create_otp_token(token, otp_token, "email")

            await user_manager.on_after_otp_email_created(user, access_token_record, otp_token_record)
            return OtpResponse(status=True, message="E-mail was sent")

        """ todo as feature """
        if "sms" in token_mfas and target_mfa_verification == "sms":
            pass

        """ todo as feature """
        if "authenticator" in token_mfas and target_mfa_verification == "authenticator":
            pass

        return OtpResponse(status=False, error="No MFA")

    class ValidateOtpTokenRequestBody(BaseModel):
        code: str
        type: str

    @router.post(
        "/otp/validate-token",
        response_model=OtpResponse,
        name=f"auth:{backend.name}.validate_otp_token",
        dependencies=[Depends(get_current_active_user)],
    )
    async def validate_token(
        request: Request,
        jsonBody: ValidateOtpTokenRequestBody,
        user_token: tuple[models.UP, str] = Depends(get_current_user_token),
        otp_manager: OtpManager[models.OTPTP] = Depends(get_otp_manager),
        strategy: Strategy[models.UP, models.ID, models.AP] = Depends(backend.get_strategy),
    ) -> OtpResponse:
        _, token = user_token
        mfa_token = jsonBody.code
        mfa_type = jsonBody.type

        otp_record = await otp_manager.find_otp_token(token, mfa_type, mfa_token, only_valid=True)

        if otp_record is not None:
            token_record = await strategy.get_token_record(token=token)
            if token_record is None:
                return OtpResponse(status=False, error="no-token")

            token_mfa_scopes = copy.deepcopy(token_record.mfa_scopes)
            token_mfa_scopes[mfa_type] = 1

            if all(value == 1 for value in token_mfa_scopes.values()):
                scopes = "approved"
            else:
                scopes = "none"

            new_token = await strategy.update_token(token_record, {"mfa_scopes": token_mfa_scopes, "scopes": scopes})
            await otp_manager.delete_record(otp_record=otp_record)

            return OtpResponse(status=True, message="Approved", access_token=new_token)

        return OtpResponse(status=False, error="no-token")

    return router
