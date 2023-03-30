from typing import Any, AsyncGenerator, Dict, cast

import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.authentication import Authenticator
from fastapi_users.router import ErrorCode, auth, get_register_router


@pytest.fixture
def app_factory(get_user_manager, mock_authentication):
    def _app_factory() -> FastAPI:
        mock_authentication_bis = get_mock_authentication(name="mock-bis")
        authenticator = Authenticator(
            [mock_authentication, mock_authentication_bis], get_user_manager
        )

        register_router = get_register_router(
            get_user_manager, User, UserCreate, authenticator
        )

        app = FastAPI()
        app.include_router(register_router)

        return app

    return _app_factory


from tests.conftest import User, UserCreate, get_mock_authentication


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    get_user_manager, get_test_client, app_factory
) -> AsyncGenerator[httpx.AsyncClient, None]:
    app = app_factory()
    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestRegister:
    async def test_empty_body(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post("/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_email(self, test_app_client: httpx.AsyncClient):
        json = {"password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, test_app_client: httpx.AsyncClient):
        json = {"email": "king.arthur@camelot.bt"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_wrong_email(self, test_app_client: httpx.AsyncClient):
        json = {"email": "king.arthur", "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_invalid_password(self, test_app_client: httpx.AsyncClient):
        json = {"email": "king.arthur@camelot.bt", "password": "g"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == {
            "code": ErrorCode.REGISTER_INVALID_PASSWORD,
            "reason": "Password should be at least 3 characters",
        }

    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(self, email, test_app_client: httpx.AsyncClient):
        json = {"email": email, "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS

    @pytest.mark.parametrize("email", ["lancelot@camelot.bt", "Lancelot@camelot.bt"])
    async def test_valid_body(self, email, test_app_client: httpx.AsyncClient):
        json = {"email": email, "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED

        data = cast(Dict[str, Any], response.json())
        assert "hashed_password" not in data
        assert "password" not in data
        assert data["id"] is not None

    async def test_valid_body_is_superuser(self, test_app_client: httpx.AsyncClient):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_superuser": True,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

    async def test_valid_body_is_active(self, test_app_client: httpx.AsyncClient):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_active": False,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True


    @pytest.mark.asyncio
    async def test_register_namespace(self, app_factory):
        assert app_factory().url_path_for("register:register") == "/register"
