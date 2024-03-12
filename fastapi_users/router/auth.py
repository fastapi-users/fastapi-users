from typing import Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users import models
from fastapi_users.authentication import (
    Authenticator,
    BaseAuthenticationBackend,
    Strategy,
)
from fastapi_users.authentication.backend import AuthenticationBackendRefresh
from fastapi_users.authentication.strategy.base import StrategyRefresh
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel


def get_auth_router(
    backend: BaseAuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification
    )

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

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
    )
    async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
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
        response = await backend.login(strategy, user)
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

    @router.post(
        "/logout", name=f"auth:{backend.name}.logout", responses=logout_responses
    )
    async def logout(
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        return await backend.logout(strategy, user, token)

    if isinstance(backend, AuthenticationBackendRefresh):
        refresh_responses: OpenAPIResponseType = {
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Wrong token",
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REFRESH_INVALID_TOKEN: {
                                "summary": "Wrong token or incorrect token format",
                                "value": {"detail": ErrorCode.REFRESH_INVALID_TOKEN},
                            },
                        }
                    }
                },
            },
            **backend.transport.get_openapi_refresh_responses_success(),
        }

        @router.post(
            "/refresh", name=f"auth:{backend.name}.refresh", responses=refresh_responses
        )
        async def refresh(
            refresh_token: str = Body(..., embed=True),
            strategy: StrategyRefresh[models.UP, models.ID] = Depends(
                backend.get_strategy
            ),
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(
                get_user_manager
            ),
        ):
            token = await backend.refresh(
                strategy=strategy,
                user_manager=user_manager,
                refresh_token=refresh_token,
            )
            if token is None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail=ErrorCode.REFRESH_INVALID_TOKEN
                )

    return router
