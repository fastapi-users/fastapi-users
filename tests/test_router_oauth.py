from typing import Any, Dict, cast

import httpx
import pytest
from fastapi import FastAPI, status
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2

from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.router.oauth import generate_state_token, get_oauth_router
from tests.conftest import AsyncMethodMocker, UserManagerMock, UserOAuthModel


@pytest.fixture
def app_factory(secret, get_user_manager_oauth, mock_authentication, oauth_client):
    def _app_factory(redirect_url: str = None) -> FastAPI:
        oauth_router = get_oauth_router(
            oauth_client,
            mock_authentication,
            get_user_manager_oauth,
            secret,
            redirect_url,
        )
        app = FastAPI()
        app.include_router(oauth_router)
        return app

    return _app_factory


@pytest.fixture
def test_app(app_factory):
    return app_factory()


@pytest.fixture
def test_app_redirect_url(app_factory):
    return app_factory("http://www.tintagel.bt/callback")


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(test_app, get_test_client):
    async for client in get_test_client(test_app):
        yield client


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client_redirect_url(test_app_redirect_url, get_test_client):
    async for client in get_test_client(test_app_redirect_url):
        yield client


@pytest.mark.router
@pytest.mark.oauth
@pytest.mark.asyncio
class TestAuthorize:
    async def test_success(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        oauth_client: BaseOAuth2,
    ):
        get_authorization_url_mock = async_method_mocker(
            oauth_client, "get_authorization_url", return_value="AUTHORIZATION_URL"
        )

        response = await test_app_client.get(
            "/authorize", params={"scopes": ["scope1", "scope2"]}
        )

        assert response.status_code == status.HTTP_200_OK
        get_authorization_url_mock.assert_called_once()

        data = response.json()
        assert "authorization_url" in data

    async def test_with_redirect_url(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client_redirect_url: httpx.AsyncClient,
        oauth_client: BaseOAuth2,
    ):
        get_authorization_url_mock = async_method_mocker(
            oauth_client, "get_authorization_url", return_value="AUTHORIZATION_URL"
        )

        response = await test_app_client_redirect_url.get(
            "/authorize", params={"scopes": ["scope1", "scope2"]}
        )

        assert response.status_code == status.HTTP_200_OK
        get_authorization_url_mock.assert_called_once()

        data = response.json()
        assert "authorization_url" in data


@pytest.mark.router
@pytest.mark.oauth
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "access_token",
    [
        ({"access_token": "TOKEN", "expires_at": 1579179542}),
        ({"access_token": "TOKEN"}),
    ],
)
class TestCallback:
    async def test_invalid_state(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        oauth_client: BaseOAuth2,
        user_oauth: UserOAuthModel,
        access_token: str,
    ):
        async_method_mocker(oauth_client, "get_access_token", return_value=access_token)
        get_id_email_mock = async_method_mocker(
            oauth_client, "get_id_email", return_value=("user_oauth1", user_oauth.email)
        )

        response = await test_app_client.get(
            "/callback",
            params={"code": "CODE", "state": "STATE"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        get_id_email_mock.assert_called_once_with("TOKEN")

    async def test_active_user(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        oauth_client: BaseOAuth2,
        user_oauth: UserOAuthModel,
        user_manager_oauth: UserManagerMock,
        access_token: str,
    ):
        state_jwt = generate_state_token({}, "SECRET")
        async_method_mocker(oauth_client, "get_access_token", return_value=access_token)
        async_method_mocker(
            oauth_client, "get_id_email", return_value=("user_oauth1", user_oauth.email)
        )
        async_method_mocker(
            user_manager_oauth, "oauth_callback", return_value=user_oauth
        )

        response = await test_app_client.get(
            "/callback",
            params={"code": "CODE", "state": state_jwt},
        )

        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["access_token"] == str(user_oauth.id)

    async def test_inactive_user(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        oauth_client: BaseOAuth2,
        inactive_user_oauth: UserOAuthModel,
        user_manager_oauth: UserManagerMock,
        access_token: str,
    ):
        state_jwt = generate_state_token({}, "SECRET")
        async_method_mocker(oauth_client, "get_access_token", return_value=access_token)
        async_method_mocker(
            oauth_client,
            "get_id_email",
            return_value=("user_oauth1", inactive_user_oauth.email),
        )
        async_method_mocker(
            user_manager_oauth, "oauth_callback", return_value=inactive_user_oauth
        )

        response = await test_app_client.get(
            "/callback",
            params={"code": "CODE", "state": state_jwt},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_redirect_url_router(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client_redirect_url: httpx.AsyncClient,
        oauth_client: BaseOAuth2,
        user_oauth: UserOAuthModel,
        user_manager_oauth: UserManagerMock,
        access_token: str,
    ):
        state_jwt = generate_state_token({}, "SECRET")
        get_access_token_mock = async_method_mocker(
            oauth_client, "get_access_token", return_value=access_token
        )
        async_method_mocker(
            oauth_client, "get_id_email", return_value=("user_oauth1", user_oauth.email)
        )
        async_method_mocker(
            user_manager_oauth, "oauth_callback", return_value=user_oauth
        )

        response = await test_app_client_redirect_url.get(
            "/callback",
            params={"code": "CODE", "state": state_jwt},
        )

        assert response.status_code == status.HTTP_200_OK

        get_access_token_mock.assert_called_once_with(
            "CODE", "http://www.tintagel.bt/callback", None
        )

        data = cast(Dict[str, Any], response.json())
        assert data["access_token"] == str(user_oauth.id)


@pytest.mark.asyncio
@pytest.mark.oauth
@pytest.mark.router
async def test_route_names(
    test_app: FastAPI, oauth_client: OAuth2, mock_authentication: AuthenticationBackend
):
    authorize_route_name = (
        f"oauth:{oauth_client.name}.{mock_authentication.name}.authorize"
    )
    assert test_app.url_path_for(authorize_route_name) == "/authorize"

    callback_route_name = (
        f"oauth:{oauth_client.name}.{mock_authentication.name}.callback"
    )
    assert test_app.url_path_for(callback_route_name) == "/callback"
