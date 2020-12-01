from typing import Any, AsyncGenerator, Dict, cast
from unittest.mock import MagicMock

import asynctest
import httpx
import jwt
import pytest
from fastapi import FastAPI, Request, status
from pydantic import UUID4

from fastapi_users.router import ErrorCode, get_register_router
from fastapi_users.user import get_activate_user, get_create_user
from fastapi_users.utils import generate_jwt
from tests.conftest import User, UserCreate, UserDB

SECRET = "SECRET"
LIFETIME = 3600
ACTIVATE_USER_TOKEN_AUDIENCE = "fastapi-users:activate"
JWT_ALGORITHM = "HS256"

activation_token_secret = SECRET
activation_token_lifetime_seconds = LIFETIME


def after_register_sync():
    return MagicMock(return_value=None)


def after_register_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[after_register_sync, after_register_async])
def after_register(request):
    return request.param()


def activation_callback_sync():
    return MagicMock(return_value=None)


def activation_callback_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[activation_callback_sync, activation_callback_async])
def activation_callback(request):
    return request.param()


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db,
    mock_authentication,
    after_register,
    activation_callback,
    get_test_client,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    create_user = get_create_user(mock_user_db, UserDB)
    activate_user = get_activate_user(mock_user_db)
    register_router = get_register_router(
        create_user,
        User,
        UserCreate,
        after_register,
        activation_callback,
        activate_user,
        activation_token_secret,
        activation_token_lifetime_seconds,
    )

    app = FastAPI()
    app.include_router(register_router)

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestRegister:
    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        response = await test_app_client.post("/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_missing_email(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        json = {"password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_missing_password(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        json = {"email": "king.arthur@camelot.bt"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_wrong_email(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        json = {"email": "king.arthur", "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_register.called is False
        assert activation_callback.called is False

    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(
        self,
        email,
        test_app_client: httpx.AsyncClient,
        after_register,
        activation_callback,
    ):
        json = {"email": email, "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS
        assert after_register.called is False
        assert activation_callback.called is False

    @pytest.mark.parametrize("email", ["lancelot@camelot.bt", "Lancelot@camelot.bt"])
    async def test_valid_body(
        self,
        email,
        test_app_client: httpx.AsyncClient,
        after_register,
        activation_callback,
    ):
        json = {"email": email, "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert after_register.called is False
        assert activation_callback.called is True
        data = cast(Dict[str, Any], response.json())
        assert "hashed_password" not in data
        assert "password" not in data
        assert data["id"] is not None

        actual_user = activation_callback.call_args[0][0]
        assert str(actual_user.id) == data["id"]
        assert str(actual_user.email) == email
        request = activation_callback.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_superuser(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_superuser": True,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert after_register.called is False
        assert activation_callback.called is True
        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

    async def test_valid_body_is_active(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_active": True,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert after_register.called is False
        assert activation_callback.called is True
        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is False

    async def test_valid_body_correct_token_produced(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert after_register.called is False
        assert activation_callback.called is True

        token = activation_callback.call_args[0][1]
        data = jwt.decode(
            token,
            activation_token_secret,
            audience=ACTIVATE_USER_TOKEN_AUDIENCE,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = data.get("user_id")
        user_uuid = UUID4(user_id)
        created_user = activation_callback.call_args[0][0]
        assert user_uuid == created_user.id


@pytest.mark.router
@pytest.mark.asyncio
class TestActivate:
    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        response = await test_app_client.post("/activate", json="")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.ACTIVATE_USER_BAD_TOKEN
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_invalid_token(
        self, test_app_client: httpx.AsyncClient, after_register, activation_callback
    ):
        token = "foo"
        response = await test_app_client.post("/activate", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.ACTIVATE_USER_BAD_TOKEN
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_valid_token_missing_user_id(
        self,
        test_app_client: httpx.AsyncClient,
        inactive_user: UserDB,
        after_register,
        activation_callback,
    ):
        created_user = inactive_user
        token_data = {"user_id": str(""), "aud": ACTIVATE_USER_TOKEN_AUDIENCE}
        token = generate_jwt(
            token_data,
            activation_token_lifetime_seconds,
            activation_token_secret,
        )
        response = await test_app_client.post("/activate", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.ACTIVATE_USER_BAD_TOKEN
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_valid_token_invalid_uuid(
        self,
        test_app_client: httpx.AsyncClient,
        inactive_user: UserDB,
        after_register,
        activation_callback,
    ):
        created_user = inactive_user
        token_data = {"user_id": str("foo"), "aud": ACTIVATE_USER_TOKEN_AUDIENCE}
        token = generate_jwt(
            token_data,
            activation_token_lifetime_seconds,
            activation_token_secret,
        )
        response = await test_app_client.post("/activate", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.ACTIVATE_USER_BAD_TOKEN
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_expired_token(
        self,
        test_app_client: httpx.AsyncClient,
        inactive_user: UserDB,
        after_register,
        activation_callback,
    ):
        activation_token_lifetime_seconds = -1
        created_user = inactive_user
        token_data = {
            "user_id": str(created_user.id),
            "aud": ACTIVATE_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            activation_token_lifetime_seconds,
            activation_token_secret,
        )
        response = await test_app_client.post("/activate", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.ACTIVATE_USER_TOKEN_EXPIRED
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_active_user(
        self,
        test_app_client: httpx.AsyncClient,
        active_user: UserDB,
        after_register,
        activation_callback,
    ):
        created_user = active_user
        token_data = {
            "user_id": str(created_user.id),
            "aud": ACTIVATE_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            activation_token_lifetime_seconds,
            activation_token_secret,
        )
        response = await test_app_client.post("/activate", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.ACTIVATE_USER_LINK_USED
        assert after_register.called is False
        assert activation_callback.called is False

    async def test_inactive_user(
        self,
        test_app_client: httpx.AsyncClient,
        inactive_user: UserDB,
        after_register,
        activation_callback,
    ):
        created_user = inactive_user
        token_data = {
            "user_id": str(created_user.id),
            "aud": ACTIVATE_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            activation_token_lifetime_seconds,
            activation_token_secret,
        )
        response = await test_app_client.post("/activate", json=token)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert after_register.called is True
        assert activation_callback.called is False
        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True
