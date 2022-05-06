from typing import Any, AsyncGenerator, Dict, cast

import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.exceptions import (
    InvalidPasswordException,
    InvalidResetPasswordToken,
    UserInactive,
    UserNotExists,
)
from fastapi_users.router import ErrorCode, get_reset_password_router
from tests.conftest import AsyncMethodMocker, UserManagerMock


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    get_user_manager, get_test_client
) -> AsyncGenerator[httpx.AsyncClient, None]:
    reset_router = get_reset_password_router(get_user_manager)

    app = FastAPI()
    app.include_router(reset_router)

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestForgotPassword:
    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, user_manager: UserManagerMock
    ):
        response = await test_app_client.post("/forgot-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.forgot_password.called is False

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, user_manager: UserManagerMock
    ):
        user_manager.get_by_email.side_effect = UserNotExists()
        json = {"email": "lancelot@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert user_manager.forgot_password.called is False

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, user_manager: UserManagerMock
    ):
        user_manager.forgot_password.side_effect = UserInactive()
        json = {"email": "percival@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED

    async def test_existing_user(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        async_method_mocker(user_manager, "forgot_password", return_value=None)
        json = {"email": "king.arthur@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.router
@pytest.mark.asyncio
class TestResetPassword:
    async def test_empty_body(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        response = await test_app_client.post("/reset-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.reset_password.called is False

    async def test_missing_token(
        self, test_app_client: httpx.AsyncClient, user_manager: UserManagerMock
    ):
        json = {"password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.reset_password.called is False

    async def test_missing_password(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        json = {"token": "foo"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.reset_password.called is False

    async def test_invalid_token(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        user_manager.reset_password.side_effect = InvalidResetPasswordToken()
        json = {"token": "foo", "password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN

    async def test_inactive_user(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        user_manager.reset_password.side_effect = UserInactive()
        json = {"token": "foo", "password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN

    async def test_invalid_password(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        user_manager.reset_password.side_effect = InvalidPasswordException(
            reason="Invalid"
        )
        json = {"token": "foo", "password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == {
            "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
            "reason": "Invalid",
        }

    async def test_valid_user_password(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        async_method_mocker(user_manager, "reset_password", return_value=None)
        json = {"token": "foo", "password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_forgot_password_namespace(get_user_manager):
    app = FastAPI()
    app.include_router(get_reset_password_router(get_user_manager))
    assert app.url_path_for("reset:forgot_password") == "/forgot-password"


@pytest.mark.asyncio
async def test_reset_password_namespace(get_user_manager):
    app = FastAPI()
    app.include_router(get_reset_password_router(get_user_manager))
    assert app.url_path_for("reset:reset_password") == "/reset-password"
