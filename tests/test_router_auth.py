from typing import Any, AsyncGenerator, Callable, Dict, cast

import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.authentication import Authenticator
from fastapi_users.router import ErrorCode, get_auth_router
from tests.conftest import MockAuthentication, UserDB


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client_factory(
    mock_user_db, mock_authentication, get_param_test_client
) -> AsyncGenerator[httpx.AsyncClient, None]:
    async def app_factory(requires_verification):

        mock_authentication_bis = MockAuthentication(name="mock-bis")
        authenticator = Authenticator(
            [mock_authentication, mock_authentication_bis], mock_user_db
        )

        mock_auth_router = get_auth_router(
            mock_authentication,
            mock_user_db,
            authenticator,
            requires_verification=requires_verification,
        )
        mock_bis_auth_router = get_auth_router(
            mock_authentication_bis,
            mock_user_db,
            authenticator,
            requires_verification=requires_verification,
        )

        app = FastAPI()
        app.include_router(mock_auth_router, prefix="/mock")
        app.include_router(mock_bis_auth_router, prefix="/mock-bis")

        return app

    async for client in get_param_test_client(app_factory):
        yield client


@pytest.mark.parametrize("requires_verification", [True, False])
@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/login", "/mock-bis/login"])
@pytest.mark.asyncio
class TestLogin:
    async def test_empty_body(
        self,
        path,
        test_app_client_factory: Callable[[Any], httpx.AsyncClient],
        requires_verification,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.post(path, data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_username(
        self, path, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        data = {"password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(
        self, path, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        data = {"username": "king.arthur@camelot.bt"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_not_existing_user(
        self, path, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        data = {"username": "lancelot@camelot.bt", "password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

    async def test_wrong_password(
        self, path, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        data = {"username": "king.arthur@camelot.bt", "password": "percival"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_valid_credentials_unverified(
        self,
        path,
        email,
        test_app_client_factory: httpx.AsyncClient,
        user: UserDB,
        requires_verification,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        data = {"username": email, "password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        if requires_verification:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = cast(Dict[str, Any], response.json())
            assert data["detail"] == ErrorCode.LOGIN_USER_NOT_VERIFIED
        else:
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {"token": str(user.id)}

    @pytest.mark.parametrize("email", ["lake.lady@camelot.bt", "Lake.Lady@camelot.bt"])
    async def test_valid_credentials_verified(
        self,
        path,
        email,
        test_app_client_factory: httpx.AsyncClient,
        verified_user: UserDB,
        requires_verification,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        data = {"username": email, "password": "excalibur"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"token": str(verified_user.id)}

    async def test_inactive_user(
        self, path, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        data = {"username": "percival@camelot.bt", "password": "angharad"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS


@pytest.mark.parametrize("requires_verification", [True, False])
@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/logout", "/mock-bis/logout"])
@pytest.mark.asyncio
class TestLogout:
    async def test_missing_token(
        self, path, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.post(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_credentials_unverified(
        self,
        mocker,
        path,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.post(
            path, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK

    async def test_valid_credentials_verified(
        self,
        mocker,
        path,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.post(
            path, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
