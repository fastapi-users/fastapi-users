from typing import Any, AsyncGenerator, Dict, cast
from unittest.mock import MagicMock

import asynctest
import httpx
import pytest
from fastapi import FastAPI, Request, status

from fastapi_users.authentication import Authenticator
from fastapi_users.router.common import ErrorCode
from fastapi_users.router.oauth import generate_state_token, get_oauth_router
from tests.conftest import MockAuthentication, UserDB

SECRET = "SECRET"


def after_register_sync():
    return MagicMock(return_value=None)


def after_register_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[after_register_sync, after_register_async])
def after_register(request):
    return request.param()


@pytest.fixture
def get_test_app_client(
    mock_user_db_oauth,
    mock_authentication,
    oauth_client,
    after_register,
    get_test_client,
):
    async def _get_test_app_client(
        redirect_url: str = None,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        mock_authentication_bis = MockAuthentication(name="mock-bis")
        authenticator = Authenticator(
            [mock_authentication, mock_authentication_bis], mock_user_db_oauth
        )

        oauth_router = get_oauth_router(
            oauth_client,
            mock_user_db_oauth,
            UserDB,
            authenticator,
            SECRET,
            redirect_url,
            after_register,
        )

        app = FastAPI()
        app.include_router(oauth_router)

        async for client in get_test_client(app):
            yield client

    return _get_test_app_client


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(get_test_app_client):
    async for client in get_test_app_client():
        yield client


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client_redirect_url(get_test_app_client):
    async for client in get_test_app_client("http://www.tintagel.bt/callback"):
        yield client


@pytest.mark.router
@pytest.mark.oauth
@pytest.mark.asyncio
class TestAuthorize:
    async def test_missing_authentication_backend(
        self, test_app_client: httpx.AsyncClient, oauth_client
    ):
        with asynctest.patch.object(oauth_client, "get_authorization_url") as mock:
            mock.return_value = "AUTHORIZATION_URL"
            response = await test_app_client.get(
                "/authorize",
                params={"scopes": ["scope1", "scope2"]},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_wrong_authentication_backend(
        self, test_app_client: httpx.AsyncClient, oauth_client
    ):
        with asynctest.patch.object(oauth_client, "get_authorization_url") as mock:
            mock.return_value = "AUTHORIZATION_URL"
            response = await test_app_client.get(
                "/authorize",
                params={
                    "authentication_backend": "foo",
                    "scopes": ["scope1", "scope2"],
                },
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_success(self, test_app_client: httpx.AsyncClient, oauth_client):
        with asynctest.patch.object(oauth_client, "get_authorization_url") as mock:
            mock.return_value = "AUTHORIZATION_URL"
            response = await test_app_client.get(
                "/authorize",
                params={
                    "authentication_backend": "mock",
                    "scopes": ["scope1", "scope2"],
                },
            )

        assert response.status_code == status.HTTP_200_OK
        mock.assert_awaited_once()

        data = response.json()
        assert "authorization_url" in data

    async def test_with_redirect_url(
        self, test_app_client_redirect_url: httpx.AsyncClient, oauth_client
    ):
        with asynctest.patch.object(oauth_client, "get_authorization_url") as mock:
            mock.return_value = "AUTHORIZATION_URL"
            response = await test_app_client_redirect_url.get(
                "/authorize",
                params={
                    "authentication_backend": "mock",
                    "scopes": ["scope1", "scope2"],
                },
            )

        assert response.status_code == status.HTTP_200_OK
        mock.assert_awaited_once()

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
        test_app_client: httpx.AsyncClient,
        access_token,
        oauth_client,
        user_oauth,
        after_register,
    ):
        with asynctest.patch.object(
            oauth_client, "get_access_token"
        ) as get_access_token_mock:
            get_access_token_mock.return_value = access_token
            with asynctest.patch.object(
                oauth_client, "get_id_email"
            ) as get_id_email_mock:
                get_id_email_mock.return_value = ("user_oauth1", user_oauth.email)
                response = await test_app_client.get(
                    "/callback",
                    params={"code": "CODE", "state": "STATE"},
                )

        get_id_email_mock.assert_awaited_once_with("TOKEN")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert after_register.called is False

    async def test_existing_user_with_oauth(
        self,
        mock_user_db_oauth,
        test_app_client: httpx.AsyncClient,
        access_token,
        oauth_client,
        user_oauth,
        after_register,
    ):
        state_jwt = generate_state_token({"authentication_backend": "mock"}, "SECRET")
        with asynctest.patch.object(
            oauth_client, "get_access_token"
        ) as get_access_token_mock:
            get_access_token_mock.return_value = access_token
            with asynctest.patch.object(
                oauth_client, "get_id_email"
            ) as get_id_email_mock:
                with asynctest.patch.object(
                    mock_user_db_oauth, "update"
                ) as user_update_mock:
                    get_id_email_mock.return_value = ("user_oauth1", user_oauth.email)
                    response = await test_app_client.get(
                        "/callback",
                        params={"code": "CODE", "state": state_jwt},
                    )

        get_id_email_mock.assert_awaited_once_with("TOKEN")
        user_update_mock.assert_awaited_once()
        data = cast(Dict[str, Any], response.json())

        assert data["token"] == str(user_oauth.id)

        assert after_register.called is False

    async def test_existing_user_without_oauth(
        self,
        mock_user_db_oauth,
        test_app_client: httpx.AsyncClient,
        access_token,
        oauth_client,
        superuser_oauth,
        after_register,
    ):
        state_jwt = generate_state_token({"authentication_backend": "mock"}, "SECRET")
        with asynctest.patch.object(
            oauth_client, "get_access_token"
        ) as get_access_token_mock:
            get_access_token_mock.return_value = access_token
            with asynctest.patch.object(
                oauth_client, "get_id_email"
            ) as get_id_email_mock:
                with asynctest.patch.object(
                    mock_user_db_oauth, "update"
                ) as user_update_mock:
                    get_id_email_mock.return_value = (
                        "superuser_oauth1",
                        superuser_oauth.email,
                    )
                    response = await test_app_client.get(
                        "/callback",
                        params={"code": "CODE", "state": state_jwt},
                    )

        get_id_email_mock.assert_awaited_once_with("TOKEN")
        user_update_mock.assert_awaited_once()
        data = cast(Dict[str, Any], response.json())

        assert data["token"] == str(superuser_oauth.id)

        assert after_register.called is False

    async def test_unknown_user(
        self,
        mock_user_db_oauth,
        test_app_client: httpx.AsyncClient,
        access_token,
        oauth_client,
        after_register,
    ):
        state_jwt = generate_state_token({"authentication_backend": "mock"}, "SECRET")
        with asynctest.patch.object(
            oauth_client, "get_access_token"
        ) as get_access_token_mock:
            get_access_token_mock.return_value = access_token
            with asynctest.patch.object(
                oauth_client, "get_id_email"
            ) as get_id_email_mock:
                with asynctest.patch.object(
                    mock_user_db_oauth, "create"
                ) as user_create_mock:
                    get_id_email_mock.return_value = (
                        "unknown_user_oauth1",
                        "galahad@camelot.bt",
                    )
                    response = await test_app_client.get(
                        "/callback",
                        params={"code": "CODE", "state": state_jwt},
                    )

        get_id_email_mock.assert_awaited_once_with("TOKEN")
        user_create_mock.assert_awaited_once()
        data = cast(Dict[str, Any], response.json())

        assert "token" in data

        assert after_register.called is True
        actual_user = after_register.call_args[0][0]
        assert str(actual_user.id) == data["token"]
        request = after_register.call_args[0][1]
        assert isinstance(request, Request)

    async def test_inactive_user(
        self,
        mock_user_db_oauth,
        test_app_client: httpx.AsyncClient,
        access_token,
        oauth_client,
        inactive_user_oauth,
        after_register,
    ):
        state_jwt = generate_state_token({"authentication_backend": "mock"}, "SECRET")
        with asynctest.patch.object(
            oauth_client, "get_access_token"
        ) as get_access_token_mock:
            get_access_token_mock.return_value = access_token
            with asynctest.patch.object(
                oauth_client, "get_id_email"
            ) as get_id_email_mock:
                get_id_email_mock.return_value = (
                    "inactive_user_oauth1",
                    inactive_user_oauth.email,
                )
                response = await test_app_client.get(
                    "/callback",
                    params={"code": "CODE", "state": state_jwt},
                )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

        assert after_register.called is False

    async def test_redirect_url_router(
        self,
        mock_user_db_oauth,
        test_app_client_redirect_url: httpx.AsyncClient,
        access_token,
        oauth_client,
        user_oauth,
    ):
        state_jwt = generate_state_token({"authentication_backend": "mock"}, "SECRET")
        with asynctest.patch.object(
            oauth_client, "get_access_token"
        ) as get_access_token_mock:
            get_access_token_mock.return_value = access_token
            with asynctest.patch.object(
                oauth_client, "get_id_email"
            ) as get_id_email_mock:
                get_id_email_mock.return_value = ("user_oauth1", user_oauth.email)
                response = await test_app_client_redirect_url.get(
                    "/callback",
                    params={"code": "CODE", "state": state_jwt},
                )

        get_access_token_mock.assert_awaited_once_with(
            "CODE", "http://www.tintagel.bt/callback"
        )
        data = cast(Dict[str, Any], response.json())

        assert data["token"] == str(user_oauth.id)
