from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from filuta_fastapi_users import models
from filuta_fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from filuta_fastapi_users.manager import BaseUserManager, UserManagerDependency
from filuta_fastapi_users.openapi import OpenAPIResponseType
from filuta_fastapi_users.router.common import ErrorCode, ErrorModel
import copy
from pydantic import BaseModel

def get_auth_router(
    backend: AuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator,
    requires_verification: bool = False,
    get_refresh_token_manager: any = None,
    refresh_token_lifetime_seconds: int = None
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                            "summary": "The user is not verified.",
                            "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_login_responses_success(),
    }
    
    class ValidateLoginRequestBody(BaseModel):
        username: str
        password: str

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
    )
    async def login(
        request: Request,
        jsonBody: ValidateLoginRequestBody,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        refresh_token_manager = Depends(get_refresh_token_manager),
    ):
        user = await user_manager.authenticate(credentials=jsonBody)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
            
        refresh_token_record = await refresh_token_manager.generate_new_token_for_user(user=user)
        refresh_token = refresh_token_record.token
        response = await backend.login(strategy=strategy, user=user, refresh_token=refresh_token)
        
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: OpenAPIResponseType = {
        **{
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
        **backend.transport.get_openapi_logout_responses_success(),
    }
    
    get_current_user_to_renew_token = authenticator.current_user_token(
        active=True, verified=requires_verification, authorized=True, ignore_expired=True
    )


    class ValidateRefreshTokenRequestBody(BaseModel):
        refresh_token: str

    @router.post(
        "/renew-access-token",
        name=f"auth:{backend.name}.renew_access_token",
    )
    async def renew_access_token(
        request: Request,
        jsonBody: ValidateRefreshTokenRequestBody,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        refresh_token_manager = Depends(get_refresh_token_manager),
        user_token: Tuple[models.UP, str] = Depends(get_current_user_to_renew_token),
    ):
        user, token = user_token
        refresh_token = jsonBody.refresh_token
        
        refresh_token_record = await refresh_token_manager.find_refresh_token(refresh_token=refresh_token, lifetime_seconds=refresh_token_lifetime_seconds)
                
        if not refresh_token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RENEW_WRONG_REFRESH_TOKEN,
            )
        
        old_token_record = await strategy.get_token_record_raw(token)
        
        if not old_token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RENEW_WRONG_ACCESS_TOKEN,
            )
    
        new_access_token_record = {
            "user_id": old_token_record.user_id,
            "token": strategy.generate_token(),
            "scopes": old_token_record.scopes,
            "mfa_scopes": old_token_record.mfa_scopes,
        }
        
        new_token_record = await strategy.insert_token(new_access_token_record)
        
        if new_token_record:
            await strategy.destroy_token(token=old_token_record.token)
        
        return JSONResponse({
            "access_token": new_token_record.token
        })
                
    
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification, authorized=True
    )

    @router.post(
        "/logout", name=f"auth:{backend.name}.logout", responses=logout_responses
    )
    async def logout(
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        logout_response = await backend.logout(strategy, user, token)
        
        return logout_response

    return router
