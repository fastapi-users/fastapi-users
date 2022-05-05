from typing import Any, AsyncGenerator, Dict, Tuple, cast

import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.authentication import Authenticator
from fastapi_users.router import ErrorCode, get_auth_router
from tests.conftest import UserModel, get_mock_authentication


@pytest.fixture
def app_factory(get_user_manager, mock_authentication):
    def _app_factory(requires_verification: bool) -> FastAPI:
        mock_authentication_bis = get_mock_authentication(name="mock-bis")
        authenticator = Authenticator(
            [mock_authentication, mock_authentication_bis], get_user_manager
        )

        mock_auth_router = get_auth_router(
            mock_authentication,
            get_user_manager,
            authenticator,
            requires_verification=requires_verification,
        )
        mock_bis_auth_router = get_auth_router(
            mock_authentication_bis,
            get_user_manager,
            authenticator,
            requires_verification=requires_verification,
        )

        app = FastAPI()
        app.include_router(mock_auth_router, prefix="/mock")
        app.include_router(mock_bis_auth_router, prefix="/mock-bis")

        return app

    return _app_factory


@pytest.fixture(
    params=[True, False], ids=["required_verification", "not_required_verification"]
)
@pytest.mark.asyncio
async def test_app_client(
    request, get_test_client, app_factory
) -> AsyncGenerator[Tuple[httpx.AsyncClient, bool], None]:
    requires_verification = request.param
    app = app_factory(requires_verification)

    async for client in get_test_client(app):
        yield client, requires_verification


@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/login", "/mock-bis/login"])
@pytest.mark.asyncio
class TestLogin:
    async def test_empty_body(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        response = await client.post(path, data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_username(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        data = {"password": "guinevere"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        data = {"username": "king.arthur@camelot.bt"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_not_existing_user(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        data = {"username": "lancelot@camelot.bt", "password": "guinevere"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

    async def test_wrong_password(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        data = {"username": "king.arthur@camelot.bt", "password": "percival"}
        response = await client.post(path, data=data)
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
        test_app_client: Tuple[httpx.AsyncClient, bool],
        user: UserModel,
    ):
        client, requires_verification = test_app_client
        data = {"username": email, "password": "guinevere"}
        response = await client.post(path, data=data)
        if requires_verification:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = cast(Dict[str, Any], response.json())
            assert data["detail"] == ErrorCode.LOGIN_USER_NOT_VERIFIED
        else:
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {
                "access_token": str(user.id),
                "token_type": "bearer",
            }

    @pytest.mark.parametrize("email", ["lake.lady@camelot.bt", "Lake.Lady@camelot.bt"])
    async def test_valid_credentials_verified(
        self,
        path,
        email,
        test_app_client: Tuple[httpx.AsyncClient, bool],
        verified_user: UserModel,
    ):
        client, _ = test_app_client
        data = {"username": email, "password": "excalibur"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "access_token": str(verified_user.id),
            "token_type": "bearer",
        }

    async def test_inactive_user(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        data = {"username": "percival@camelot.bt", "password": "angharad"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS


@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/logout", "/mock-bis/logout"])
@pytest.mark.asyncio
class TestLogout:
    async def test_missing_token(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        response = await client.post(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_credentials_unverified(
        self,
        mocker,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
        user: UserModel,
    ):
        client, requires_verification = test_app_client
        response = await client.post(
            path, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_403_FORBIDDEN
        else:
            assert response.status_code == status.HTTP_200_OK

    async def test_valid_credentials_verified(
        self,
        mocker,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
        verified_user: UserModel,
    ):
        client, _ = test_app_client
        response = await client.post(
            path, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
@pytest.mark.router
async def test_route_names(app_factory, mock_authentication):
    app = app_factory(False)
    login_route_name = f"auth:{mock_authentication.name}.login"
    assert app.url_path_for(login_route_name) == "/mock/login"

    logout_route_name = f"auth:{mock_authentication.name}.logout"
    assert app.url_path_for(logout_route_name) == "/mock/logout"
