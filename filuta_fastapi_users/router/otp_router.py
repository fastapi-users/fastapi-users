from typing import Tuple
import copy

from fastapi import APIRouter, Depends, Request, status


from filuta_fastapi_users import models
from filuta_fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from filuta_fastapi_users.manager import BaseUserManager, UserManagerDependency

from filuta_fastapi_users.authentication.mfa.base import generate_otp_token
from pydantic import BaseModel

def get_otp_router(
    backend: AuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator,
    get_otp_token_db: any = None
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=True, optional=False
    )
    
    get_current_active_user = authenticator.current_user(
        active=True, verified=False, optional=False
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
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        
        query_params = request.query_params
        target_mfa_verification = query_params.get("mfa_type", "")
        
        token_record = await strategy.get_token_record(token=token)
        token_mfas = token_record.mfa_scopes
        
        if "email" in token_mfas and target_mfa_verification == "email":
            
            otp_token = generate_otp_token()
            otp_record = await strategy.create_otp_email_token(access_token=token, mfa_token=otp_token)
            """ await user_manager.on_after_otp_email_created(user=user, token_record=token_record, otp_record=otp_record) """
            return {"status": True, "message": "E-mail was sent"}
        
        """ todo as feature """
        if "sms" in token_mfas and target_mfa_verification == "sms":
            pass
        
        """ todo as feature """
        if "authenticator" in token_mfas and target_mfa_verification == "authenticator":
            pass 
        
        return {"status": False, "message": "No MFA"}


    class ValidateOtpTokenRequestBody(BaseModel):
        code: str
        type: str

    @router.post(
        "/otp/validate_token",
        name=f"auth:{backend.name}.validate_otp_token",
        dependencies=[Depends(get_current_active_user)],
    )
    async def send_otp_token(
        request: Request,
        jsonBody: ValidateOtpTokenRequestBody,
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        mfa_token = jsonBody.code
        mfa_type = jsonBody.type
        
        """ todo get_otp_token_db """
        
        
        otp_record = await strategy.find_otp_token(access_token = token, mfa_type=mfa_type, mfa_token=mfa_token)
        
        if otp_record:
            
            token_record = await strategy.get_token_record(token=token)
            token_mfa_scopes = copy.deepcopy(token_record.mfa_scopes)
            token_mfa_scopes[mfa_type] = 1
            new_token = await strategy.update_token(access_token=token_record, data={"mfa_scopes": token_mfa_scopes})
            
            return {"status": True, "message": "Approved", "access_token": new_token}
                    
        return {"status": False}
        
    return router