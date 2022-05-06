from typing import Any, AsyncGenerator, Dict, cast

import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.exceptions import (
    InvalidVerifyToken,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from fastapi_users.router import ErrorCode, get_verify_router
from tests.conftest import AsyncMethodMocker, User, UserManagerMock, UserModel


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    get_user_manager,
    get_test_client,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    verify_router = get_verify_router(get_user_manager, User)

    app = FastAPI()
    app.include_router(verify_router)

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestVerifyTokenRequest:
    async def test_empty_body(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        response = await test_app_client.post("/request-verify-token", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.request_verify.called is False

    async def test_wrong_email(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        json = {"email": "king.arthur"}
        response = await test_app_client.post("/request-verify-token", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.request_verify.called is False

    async def test_user_not_exists(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        user_manager.get_by_email.side_effect = UserNotExists()
        json = {"email": "user@example.com"}
        response = await test_app_client.post("/request-verify-token", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert user_manager.request_verify.called is False

    async def test_user_inactive(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
        user: UserModel,
    ):
        async_method_mocker(user_manager, "get_by_email", return_value=user)
        user_manager.request_verify.side_effect = UserInactive()
        json = {"email": "user@example.com"}
        response = await test_app_client.post("/request-verify-token", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED

    async def test_user_already_verified(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
        user: UserModel,
    ):
        async_method_mocker(user_manager, "get_by_email", return_value=user)
        user_manager.request_verify.side_effect = UserAlreadyVerified()
        json = {"email": "user@example.com"}
        response = await test_app_client.post("/request-verify-token", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED

    async def test_user_not_verified(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
        user: UserModel,
    ):
        async_method_mocker(user_manager, "get_by_email", return_value=user)
        async_method_mocker(user_manager, "request_verify", return_value=None)
        json = {"email": "user@example.com"}
        response = await test_app_client.post("/request-verify-token", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED

    async def test_token_namespace(
        self,
        get_user_manager,
    ):
        verify_router = get_verify_router(
            get_user_manager,
            User,
        )

        app = FastAPI()
        app.include_router(verify_router)
        assert app.url_path_for("verify:request-token") == "/request-verify-token"


@pytest.mark.router
@pytest.mark.asyncio
class TestVerify:
    async def test_empty_body(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        response = await test_app_client.post("/verify", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.verify.called is False

    async def test_invalid_verify_token(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        user_manager.verify.side_effect = InvalidVerifyToken()
        response = await test_app_client.post("/verify", json={"token": "foo"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN

    async def test_user_not_exists(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        user_manager.verify.side_effect = UserNotExists()
        response = await test_app_client.post("/verify", json={"token": "foo"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN

    async def test_user_already_verified(
        self,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
    ):
        user_manager.verify.side_effect = UserAlreadyVerified()
        response = await test_app_client.post("/verify", json={"token": "foo"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_ALREADY_VERIFIED

    async def test_success(
        self,
        async_method_mocker: AsyncMethodMocker,
        test_app_client: httpx.AsyncClient,
        user_manager: UserManagerMock,
        user: UserModel,
    ):
        async_method_mocker(user_manager, "verify", return_value=user)
        response = await test_app_client.post("/verify", json={"token": "foo"})

        assert response.status_code == status.HTTP_200_OK
        data = cast(Dict[str, Any], response.json())
        assert data["id"] == str(user.id)

    async def test_verify_namespace(
        self,
        get_user_manager,
    ):
        verify_router = get_verify_router(
            get_user_manager,
            User,
        )

        app = FastAPI()
        app.include_router(verify_router)
        assert app.url_path_for("verify:verify") == "/verify"
