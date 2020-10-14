from typing import Any, AsyncGenerator, Dict, cast
from unittest.mock import MagicMock

import asynctest
import httpx
import pytest
from fastapi import FastAPI, Request, status

from fastapi_users.router import ErrorCode, get_register_router
from tests.conftest import User, UserCreate, UserDB

SECRET = "SECRET"
LIFETIME = 3600


def after_register_sync():
    return MagicMock(return_value=None)


def after_register_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[after_register_sync, after_register_async])
def after_register(request):
    return request.param()


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db, mock_authentication, after_register, get_test_client
) -> AsyncGenerator[httpx.AsyncClient, None]:
    register_router = get_register_router(
        mock_user_db,
        User,
        UserCreate,
        UserDB,
        after_register,
    )

    app = FastAPI()
    app.include_router(register_router)

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestRegister:
    async def test_empty_body(self, test_app_client: httpx.AsyncClient, after_register):
        response = await test_app_client.post("/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False

    async def test_missing_email(
        self, test_app_client: httpx.AsyncClient, after_register
    ):
        json = {"password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False

    async def test_missing_password(
        self, test_app_client: httpx.AsyncClient, after_register
    ):
        json = {"email": "king.arthur@camelot.bt"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False

    async def test_wrong_email(
        self, test_app_client: httpx.AsyncClient, after_register
    ):
        json = {"email": "king.arthur", "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False

    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(
        self, email, test_app_client: httpx.AsyncClient, after_register
    ):
        json = {"email": email, "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS
        assert after_register.called is False

    @pytest.mark.parametrize("email", ["lancelot@camelot.bt", "Lancelot@camelot.bt"])
    async def test_valid_body(
        self, email, test_app_client: httpx.AsyncClient, after_register
    ):
        json = {"email": email, "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert after_register.called is True

        data = cast(Dict[str, Any], response.json())
        assert "hashed_password" not in data
        assert "password" not in data
        assert data["id"] is not None

        actual_user = after_register.call_args[0][0]
        assert str(actual_user.id) == data["id"]
        assert str(actual_user.email) == email
        request = after_register.call_args[0][1]
        assert isinstance(request, Request)

    async def test_valid_body_is_superuser(
        self, test_app_client: httpx.AsyncClient, after_register
    ):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_superuser": True,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert after_register.called is True

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

    async def test_valid_body_is_active(
        self, test_app_client: httpx.AsyncClient, after_register
    ):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_active": False,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert after_register.called is True

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True
