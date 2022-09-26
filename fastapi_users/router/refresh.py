from fastapi import APIRouter, Depends, Form, HTTPException, Response, status

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, Strategy
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.scopes import SystemScope


class OAuth2RefreshTokenForm(object):
    def __init__(
        self,
        grant_type: str = Form(
            default="refresh_token", regex="refresh_token", example="refresh_token"
        ),
        refresh_token: str = Form(...),
        scope: str = Form(""),
    ):
        self.grant_type = grant_type
        self.refresh_token = refresh_token
        self.scopes = scope.split()


def get_refresh_router(
    backend: AuthenticationBackend[models.UP, models.ID],
    get_user_manager: UserManagerDependency[models.UP, models.ID],
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

    @router.post(
        "/refresh",
        name=f"auth:{backend.name}.refresh",
        responses=login_responses,
        response_model=backend.transport.login_response_model,
        response_model_exclude_none=True,
    )
    async def refresh(  # type: ignore
        response: Response,
        form_data: OAuth2RefreshTokenForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy = Depends(backend.get_strategy),
    ):
        if not backend.refresh_token_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="refresh_tokens_not_allowed",
            )

        token_data = await strategy.read_token(form_data.refresh_token, user_manager)
        if token_data:
            if (
                token_data.user
                and SystemScope.REFRESH in token_data.scopes
                and not token_data.expired
            ):
                return await backend.login(
                    strategy,
                    token_data.user,
                    response,
                    token_data.last_authenticated,
                )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_grant",
        )

    return router
