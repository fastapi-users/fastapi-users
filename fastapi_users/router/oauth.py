from typing import Any, Dict, List, Optional, Tuple

import jwt
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token
from pydantic import BaseModel

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, Strategy
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel

STATE_TOKEN_AUDIENCE = "fastapi-users:oauth-state"


class OAuthAuthorizationCodeRequestQuery:
    """
    OAuth 2.0 Authorization Request (Authorization Code Grant) as per RFC 6749
    https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1
    """

    def __init__(
        self,
        response_type: str = Query(..., regex="code"),
        client_id: str = Query(...),
        redirect_uri: Optional[str] = Query(None),
        scope: str = Query(""),
        state: Optional[str] = Query(None),
    ):
        self.response_type = response_type
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scope.split()
        self.state = state


class OAuthAuthorizationCodeTokenForm:
    """
    OAuth 2.0 Access Token Request (Authorization Code Grant) as per RFC 6749
    https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.3
    """

    def __init__(
        self,
        grant_type: str = Form(..., regex="authorization_code"),
        code: str = Form(...),
        redirect_uri: Optional[str] = Form(None),
        client_id: Optional[str] = Form(None),
    ):
        self.grant_type = grant_type
        self.code = code
        self.redirect_uri = redirect_uri
        self.client_id = client_id


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str


def generate_state_token(
    data: Dict[str, str], secret: SecretType, lifetime_seconds: int = 3600
) -> str:
    data["aud"] = STATE_TOKEN_AUDIENCE
    return generate_jwt(data, secret, lifetime_seconds)


def get_oauth_router(
    oauth_client: BaseOAuth2,
    backend: AuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UC, models.UD],
    state_secret: SecretType,
    redirect_url: str = None,
) -> APIRouter:
    """Generate a router with the OAuth routes."""
    router = APIRouter()
    callback_route_name = f"oauth:{oauth_client.name}.{backend.name}.callback"

    if redirect_url is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            redirect_url=redirect_url,
        )
    else:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            route_name=callback_route_name,
        )

    async def do_oauth_login(
        request: Request,
        response: Response,
        user_manager: BaseUserManager[models.UC, models.UD],
        strategy: Strategy[models.UC, models.UD],
        token: OAuth2Token,
    ) -> Any:
        account_id, account_email = await oauth_client.get_id_email(
            token["access_token"]
        )

        new_oauth_account = models.BaseOAuthAccount(
            oauth_name=oauth_client.name,
            access_token=token["access_token"],
            expires_at=token.get("expires_at"),
            refresh_token=token.get("refresh_token"),
            account_id=account_id,
            account_email=account_email,
        )

        user = await user_manager.oauth_callback(new_oauth_account, request)

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

        # Authenticate
        return await backend.login(strategy, user, response)

    @router.get(
        "/authorize",
        name=f"oauth:{oauth_client.name}.{backend.name}.authorize",
        response_model=OAuth2AuthorizeResponse,
    )
    async def authorize(  # type: ignore
        request: Request, scopes: List[str] = Query(None)
    ) -> OAuth2AuthorizeResponse:
        if redirect_url is not None:
            authorize_redirect_url = redirect_url
        else:
            authorize_redirect_url = request.url_for(callback_route_name)

        state_data: Dict[str, str] = {}
        state = generate_state_token(state_data, state_secret)
        authorization_url = await oauth_client.get_authorization_url(
            authorize_redirect_url,
            state,
            scopes,
        )

        return OAuth2AuthorizeResponse(authorization_url=authorization_url)

    @router.get(
        "/callback",
        name=callback_route_name,
        description="The response varies based on the authentication backend used.",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            "INVALID_STATE_TOKEN": {
                                "summary": "Invalid state token.",
                                "value": None,
                            },
                            ErrorCode.LOGIN_BAD_CREDENTIALS: {
                                "summary": "User is inactive.",
                                "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                            },
                        }
                    }
                },
            },
        },
    )
    async def callback(  # type: ignore
        request: Request,
        response: Response,
        access_token_state: Tuple[OAuth2Token, str] = Depends(
            oauth2_authorize_callback
        ),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
        strategy: Strategy[models.UC, models.UD] = Depends(backend.get_strategy),
    ):
        token, state = access_token_state

        try:
            decode_jwt(state, state_secret, [STATE_TOKEN_AUDIENCE])
        except jwt.DecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return await do_oauth_login(request, response, user_manager, strategy, token)

    @router.get(
        "/oauth-authorize",
        name=f"oauth:{oauth_client.name}.{backend.name}.oauth-authorize",
        response_class=RedirectResponse,
        status_code=302,
    )
    async def oauth_authorize(  # type: ignore
        query: OAuthAuthorizationCodeRequestQuery = Depends(),
    ) -> str:
        return await oauth_client.get_authorization_url(
            query.redirect_uri,
            query.state,
            query.scopes,
        )

    @router.post(
        "/oauth-token",
        name=f"oauth:{oauth_client.name}.{backend.name}.oauth-token",
    )
    async def oauth_token(  # type: ignore
        request: Request,
        response: Response,
        form: OAuthAuthorizationCodeTokenForm = Depends(),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
        strategy: Strategy[models.UC, models.UD] = Depends(backend.get_strategy),
    ):
        token = await oauth_client.get_access_token(form.code, form.redirect_uri)

        return await do_oauth_login(request, response, user_manager, strategy, token)

    return router
