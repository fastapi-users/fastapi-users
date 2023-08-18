from typing import Tuple
import copy

from fastapi import APIRouter, Depends, Request, status


from filuta_fastapi_users import models
from filuta_fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from filuta_fastapi_users.manager import BaseUserManager, UserManagerDependency

from pydantic import BaseModel

def get_otp_router(
    backend: AuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator,
    get_otp_manager: any = None,
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification, authorized=False
    )
    
    get_current_active_user = authenticator.current_user(
        active=True, verified=requires_verification, authorized=False
    )

    @router.post(
        "/otp/send_token",
        name=f"auth:{backend.name}.send_otp_token",
        dependencies=[Depends(get_current_active_user)],
    )
    async def send_otp_token(
        request: Request,
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        otp_manager = Depends(get_otp_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        
        query_params = request.query_params
        target_mfa_verification = query_params.get("mfa_type", "")
        
        access_token_record = await strategy.get_token_record(token=token)
        token_mfas = access_token_record.mfa_scopes
        
        if "email" in token_mfas and target_mfa_verification == "email":
            
            already_obtained = await otp_manager.user_has_issued_token(access_token = token, mfa_type=target_mfa_verification)
            otp_token = otp_manager.generate_otp_token()
            
            if already_obtained:
                await otp_manager.delete_record(item=already_obtained)
                
            otp_token_record = await otp_manager.create_otp_token(access_token=token, mfa_token=otp_token, mfa_type="email")
            
            await user_manager.on_after_otp_email_created(user=user, access_token_record=access_token_record, otp_token_record=otp_token_record)
            return {"status": True, "message": "E-mail was sent"}
        
        """ todo as feature """
        if "sms" in token_mfas and target_mfa_verification == "sms":
            pass
        
        """ todo as feature """
        if "authenticator" in token_mfas and target_mfa_verification == "authenticator":
            pass 
        
        return {"status": False, "error": "no-mfa-method"}


    class ValidateOtpTokenRequestBody(BaseModel):
        code: str
        type: str

    @router.post(
        "/otp/validate_token",
        name=f"auth:{backend.name}.validate_otp_token",
        dependencies=[Depends(get_current_active_user)],
    )
    async def validate_token(
        request: Request,
        jsonBody: ValidateOtpTokenRequestBody,
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        otp_manager = Depends(get_otp_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        mfa_token = jsonBody.code
        mfa_type = jsonBody.type
        
        otp_record = await otp_manager.find_otp_token(access_token = token, mfa_type=mfa_type, mfa_token=mfa_token, only_valid=True)
        
        if otp_record:
            
            token_record = await strategy.get_token_record(token=token)
            token_mfa_scopes = copy.deepcopy(token_record.mfa_scopes)
            token_mfa_scopes[mfa_type] = 1

            if all(value == 1 for value in token_mfa_scopes.values()):
                scopes = "approved"
            else:
                scopes = "none"
            
            new_token = await strategy.update_token(access_token=token_record, data={"mfa_scopes": token_mfa_scopes, "scopes": scopes})
            await otp_manager.delete_record(item=otp_record)
            
            return {"status": True, "access_token": new_token}
                    
        return {"status": False, "error": "no-token"}
        
    return router