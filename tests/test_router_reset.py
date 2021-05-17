from typing import Any, AsyncGenerator, Dict, cast
from unittest.mock import MagicMock

import asynctest
import httpx
import jwt
import pytest
from fastapi import FastAPI, Request, status

from fastapi_users.router import ErrorCode, get_reset_password_router
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt
from tests.conftest import UserDB

SECRET = "SECRET"
LIFETIME = 3600


@pytest.fixture
def forgot_password_token():
    def _forgot_password_token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:reset"}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(data, SECRET, lifetime, JWT_ALGORITHM)

    return _forgot_password_token


def after_forgot_password_sync():
    return MagicMock(return_value=None)


def after_forgot_password_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[after_forgot_password_sync, after_forgot_password_async])
def after_forgot_password(request):
    return request.param()


def after_reset_password_sync():
    return MagicMock(return_value=None)


def after_reset_password_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[after_reset_password_sync, after_reset_password_async])
def after_reset_password(request):
    return request.param()


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db,
    after_forgot_password,
    after_reset_password,
    get_test_client,
    validate_password,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    reset_router = get_reset_password_router(
        mock_user_db,
        SECRET,
        LIFETIME,
        after_forgot_password,
        after_reset_password,
        validate_password,
    )

    app = FastAPI()
    app.include_router(reset_router)

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestForgotPassword:
    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, after_forgot_password
    ):
        response = await test_app_client.post("/forgot-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_forgot_password.called is False

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, after_forgot_password
    ):
        json = {"email": "lancelot@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert after_forgot_password.called is False

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, after_forgot_password
    ):
        json = {"email": "percival@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert after_forgot_password.called is False

    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(
        self, email, test_app_client: httpx.AsyncClient, after_forgot_password, user
    ):
        json = {"email": email}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert after_forgot_password.called is True

        actual_user = after_forgot_password.call_args[0][0]
        assert actual_user.id == user.id
        actual_token = after_forgot_password.call_args[0][1]
        decoded_token = jwt.decode(
            actual_token,
            SECRET,
            audience="fastapi-users:reset",
            algorithms=[JWT_ALGORITHM],
        )
        assert decoded_token["user_id"] == str(user.id)
        request = after_forgot_password.call_args[0][2]
        assert isinstance(request, Request)


@pytest.mark.router
@pytest.mark.asyncio
class TestResetPassword:
    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, after_reset_password
    ):
        response = await test_app_client.post("/reset-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_reset_password.called is False

    async def test_missing_token(
        self, test_app_client: httpx.AsyncClient, after_reset_password
    ):
        json = {"password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_reset_password.called is False

    async def test_missing_password(
        self, test_app_client: httpx.AsyncClient, after_reset_password
    ):
        json = {"token": "foo"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_reset_password.called is False

    async def test_invalid_token(
        self, test_app_client: httpx.AsyncClient, after_reset_password
    ):
        json = {"token": "foo", "password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN
        assert after_reset_password.called is False

    async def test_valid_token_missing_user_id_payload(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
        after_reset_password,
    ):
        mocker.spy(mock_user_db, "update")

        json = {"token": forgot_password_token(), "password": "holygrail"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN
        assert mock_user_db.update.called is False
        assert after_reset_password.called is False

    async def test_valid_token_invalid_uuid(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
        after_reset_password,
    ):
        mocker.spy(mock_user_db, "update")

        json = {"token": forgot_password_token("foo"), "password": "holygrail"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN
        assert mock_user_db.update.called is False
        assert after_reset_password.called is False

    async def test_inactive_user(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
        inactive_user: UserDB,
        after_reset_password,
    ):
        mocker.spy(mock_user_db, "update")

        json = {
            "token": forgot_password_token(inactive_user.id),
            "password": "holygrail",
        }
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN
        assert mock_user_db.update.called is False
        assert after_reset_password.called is False

    async def test_invalid_password(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
        user: UserDB,
        after_reset_password,
        validate_password,
    ):
        mocker.spy(mock_user_db, "update")

        json = {
            "token": forgot_password_token(user.id),
            "password": "h",
        }
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == {
            "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
            "reason": "Password should be at least 3 characters",
        }
        validate_password.assert_called_with("h", user)
        assert mock_user_db.update.called is False
        assert after_reset_password.called is False

    async def test_existing_user(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
        user: UserDB,
        after_reset_password,
    ):
        mocker.spy(mock_user_db, "update")
        current_hashed_password = user.hashed_password

        json = {"token": forgot_password_token(user.id), "password": "holygrail"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_password

        assert after_reset_password.called is True
        actual_user = after_reset_password.call_args[0][0]
        assert actual_user.id == updated_user.id
        request = after_reset_password.call_args[0][1]
        assert isinstance(request, Request)
