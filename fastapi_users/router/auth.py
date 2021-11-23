from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel


class LoginBadCredentials(BaseModel):
    detail: ErrorCode.LOGIN_BAD_CREDENTIALS


class LoginUserNotVerified(BaseModel):
    detail: ErrorCode.LOGIN_USER_NOT_VERIFIED


def get_auth_router(
    backend: BaseAuthentication,
    get_user_manager: UserManagerDependency[models.UC, models.UD],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    get_current_user = authenticator.current_user(
        active=True, verified=requires_verification
    )

    login_responses = {
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
        **backend.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login",
        name="auth:login",
        responses=login_responses,
    )
    async def login(
        response: Response,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        user = await user_manager.authenticate(credentials)

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
        return await backend.get_login_response(user, response, user_manager)

    if backend.logout:
        logout_responses = {
            **{
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user."
                }
            },
            **backend.get_openapi_logout_responses_success(),
        }

        @router.post("/logout", name="auth:logout", responses=logout_responses)
        async def logout(
            response: Response,
            user=Depends(get_current_user),
            user_manager: BaseUserManager[models.UC, models.UD] = Depends(
                get_user_manager
            ),
        ):
            return await backend.get_logout_response(user, response, user_manager)

    return router
