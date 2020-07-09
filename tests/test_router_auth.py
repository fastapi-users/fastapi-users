from typing import cast, Dict, Any

import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.authentication import Authenticator
from fastapi_users.router import ErrorCode, get_auth_router
from tests.conftest import MockAuthentication, UserDB


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db, mock_authentication, get_test_client
) -> httpx.AsyncClient:
    mock_authentication_bis = MockAuthentication(name="mock-bis")
    authenticator = Authenticator(
        [mock_authentication, mock_authentication_bis], mock_user_db
    )

    mock_auth_router = get_auth_router(mock_authentication, mock_user_db, authenticator)
    mock_bis_auth_router = get_auth_router(
        mock_authentication_bis, mock_user_db, authenticator
    )

    app = FastAPI()
    app.include_router(mock_auth_router, prefix="/mock")
    app.include_router(mock_bis_auth_router, prefix="/mock-bis")

    return await get_test_client(app)


@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/login", "/mock-bis/login"])
@pytest.mark.asyncio
class TestLogin:
    async def test_empty_body(self, path, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post(path, data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_username(self, path, test_app_client: httpx.AsyncClient):
        data = {"password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "king.arthur@camelot.bt"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_not_existing_user(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "lancelot@camelot.bt", "password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

    async def test_wrong_password(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "king.arthur@camelot.bt", "password": "percival"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_valid_credentials(
        self, path, email, test_app_client: httpx.AsyncClient, user: UserDB
    ):
        data = {"username": email, "password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"token": str(user.id)}

    async def test_inactive_user(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "percival@camelot.bt", "password": "angharad"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS


@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/logout", "/mock-bis/logout"])
@pytest.mark.asyncio
class TestLogout:
    async def test_missing_token(self, path, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_credentials(
        self, mocker, path, test_app_client: httpx.AsyncClient, user: UserDB
    ):
        response = await test_app_client.post(
            path, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
