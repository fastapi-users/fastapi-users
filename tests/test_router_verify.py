from typing import Any, AsyncGenerator, Dict, cast
from unittest.mock import MagicMock

import asynctest
import httpx
import pytest
from fastapi import FastAPI, Request, status

from fastapi_users.router import ErrorCode, get_verify_router
from fastapi_users.user import get_get_user, get_verify_user
from fastapi_users.utils import generate_jwt
from tests.conftest import User, UserDB

SECRET = "SECRET"
LIFETIME = 3600
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"
JWT_ALGORITHM = "HS256"

verification_token_secret = SECRET
verification_token_lifetime_seconds = LIFETIME


def after_verification_sync():
    return MagicMock(return_value=None)


def after_verification_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[after_verification_sync, after_verification_async])
def after_verification(request):
    return request.param()


def after_verification_request_sync():
    return MagicMock(return_value=None)


def after_verification_request_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(
    params=[after_verification_request_sync, after_verification_request_async]
)
def after_verification_request(request):
    return request.param()


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db,
    mock_authentication,
    after_verification_request,
    after_verification,
    get_test_client,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    verify_user = get_verify_user(mock_user_db)
    get_user = get_get_user(mock_user_db)
    verify_router = get_verify_router(
        verify_user,
        get_user,
        User,
        after_verification_request,
        verification_token_secret,
        verification_token_lifetime_seconds,
        after_verification,
    )

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
        after_verification_request,
        after_verification,
    ):
        response = await test_app_client.post("/request_verify_token", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_verification_request.called is False

    async def test_wrong_email(
        self,
        test_app_client: httpx.AsyncClient,
        after_verification_request,
        after_verification,
    ):
        json = {"email": "king.arthur"}
        response = await test_app_client.post("/request_verify_token", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert after_verification_request.called is False

    async def test_user_not_exists(
        self,
        test_app_client: httpx.AsyncClient,
        after_verification_request,
        after_verification,
    ):
        json = {"email": "user@example.com"}
        response = await test_app_client.post("/request_verify_token", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_NOT_EXISTS
        assert after_verification_request.called is False

    async def test_user_verified_valid_request(
        self,
        test_app_client: httpx.AsyncClient,
        verified_user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = verified_user
        json = {"email": input_user.email}
        response = await test_app_client.post("/request_verify_token", json=json)
        assert after_verification_request.called is False
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_ALREADY_VERIFIED

    async def test_user_inactive_valid_request(
        self,
        test_app_client: httpx.AsyncClient,
        inactive_user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = inactive_user
        json = {"email": input_user.email}
        response = await test_app_client.post("/request_verify_token", json=json)
        assert after_verification_request.called is False
        assert response.status_code == status.HTTP_202_ACCEPTED

    async def test_user_active_valid_request(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = user
        json = {"email": input_user.email}
        response = await test_app_client.post("/request_verify_token", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert after_verification_request.called is True
        actual_user = after_verification_request.call_args[0][0]
        token = after_verification_request.call_args[0][1]


@pytest.mark.router
@pytest.mark.asyncio
class TestVerify:
    async def test_empty_body(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        response = await test_app_client.post("/verify", json="")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN
        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_invalid_token(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        token = "foo"
        response = await test_app_client.post("/verify", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN
        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_valid_token_missing_user_id(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = user
        token_data = {
            "user_id": str(""),
            "email": str(input_user.email),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN
        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_valid_token_missing_email(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = user
        token_data = {
            "user_id": str(input_user.id),
            "email": str(""),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN
        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_valid_token_invalid_uuid(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = user
        token_data = {
            "user_id": str("foo"),
            "email": str(input_user.email),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN
        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_valid_token_invalid_email(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = user
        token_data = {
            "user_id": str(input_user.id),
            "email": str("foo"),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_BAD_TOKEN
        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_expired_token(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        verification_token_lifetime_seconds = -1
        input_user = user
        token_data = {
            "user_id": str(input_user.id),
            "email": str(input_user.email),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_TOKEN_EXPIRED
        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_inactive_user(
        self,
        test_app_client: httpx.AsyncClient,
        inactive_user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = inactive_user
        token_data = {
            "user_id": str(input_user.id),
            "email": str(input_user.email),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert after_verification.called is True
        assert after_verification_request.called is False
        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is False

    async def test_verified_user(
        self,
        test_app_client: httpx.AsyncClient,
        verified_user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = verified_user
        token_data = {
            "user_id": str(input_user.id),
            "email": str(input_user.email),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.VERIFY_USER_ALREADY_VERIFIED

        assert after_verification.called is False
        assert after_verification_request.called is False

    async def test_active_user(
        self,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_verification_request,
        after_verification,
    ):
        input_user = user
        token_data = {
            "user_id": str(input_user.id),
            "email": str(input_user.email),
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            token_data,
            verification_token_lifetime_seconds,
            verification_token_secret,
        )
        response = await test_app_client.post("/verify", json=token)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert after_verification.called is True
        assert after_verification_request.called is False
        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True
