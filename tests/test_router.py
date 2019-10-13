import asyncio
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import FastAPI
from starlette import status
from starlette.testclient import TestClient

from fastapi_users.models import BaseUser, BaseUserDB
from fastapi_users.router import get_user_router
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt

SECRET = "SECRET"
LIFETIME = 3600


@pytest.fixture
def forgot_password_token():
    def _forgot_password_token(user_id, lifetime=LIFETIME):
        data = {"user_id": user_id, "aud": "fastapi-users:reset"}
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _forgot_password_token


@pytest.fixture()
def on_after_forgot_password_sync():
    on_after_forgot_password_mock = MagicMock(return_value=None)
    return on_after_forgot_password_mock


@pytest.fixture()
def on_after_forgot_password_async():
    on_after_forgot_password_mock = MagicMock(return_value=asyncio.Future())
    on_after_forgot_password_mock.return_value.set_result(None)
    return on_after_forgot_password_mock


@pytest.fixture
def get_test_app_client(mock_user_db, mock_authentication):
    def _get_test_app_client(on_after_forgot_password) -> TestClient:
        class User(BaseUser):
            pass

        userRouter = get_user_router(
            mock_user_db,
            User,
            mock_authentication,
            on_after_forgot_password,
            SECRET,
            LIFETIME,
        )

        app = FastAPI()
        app.include_router(userRouter)

        return TestClient(app)

    return _get_test_app_client


@pytest.fixture
def test_app_client(get_test_app_client, on_after_forgot_password_sync):
    return get_test_app_client(on_after_forgot_password_sync)


@pytest.fixture
def test_app_client_async(get_test_app_client, on_after_forgot_password_async):
    return get_test_app_client(on_after_forgot_password_async)


class TestRegister:
    def test_empty_body(self, test_app_client: TestClient):
        response = test_app_client.post("/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_password(self, test_app_client: TestClient):
        json = {"email": "king.arthur@camelot.bt"}
        response = test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_wrong_email(self, test_app_client: TestClient):
        json = {"email": "king.arthur", "password": "guinevere"}
        response = test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_valid_body(self, test_app_client: TestClient):
        json = {"email": "king.arthur@camelot.bt", "password": "guinevere"}
        response = test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert "hashed_password" not in response_json
        assert "password" not in response_json
        assert "id" in response_json


class TestLogin:
    def test_empty_body(self, test_app_client: TestClient):
        response = test_app_client.post("/login", data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_username(self, test_app_client: TestClient):
        data = {"password": "guinevere"}
        response = test_app_client.post("/login", data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_password(self, test_app_client: TestClient):
        data = {"username": "king.arthur@camelot.bt"}
        response = test_app_client.post("/login", data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_not_existing_user(self, test_app_client: TestClient):
        data = {"username": "lancelot@camelot.bt", "password": "guinevere"}
        response = test_app_client.post("/login", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_wrong_password(self, test_app_client: TestClient):
        data = {"username": "king.arthur@camelot.bt", "password": "percival"}
        response = test_app_client.post("/login", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_valid_credentials(self, test_app_client: TestClient, user: BaseUserDB):
        data = {"username": "king.arthur@camelot.bt", "password": "guinevere"}
        response = test_app_client.post("/login", data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"token": user.id}

    def test_inactive_user(self, test_app_client: TestClient):
        data = {"username": "percival@camelot.bt", "password": "angharad"}
        response = test_app_client.post("/login", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestForgotPassword:
    def test_empty_body(
        self, test_app_client: TestClient, on_after_forgot_password_sync
    ):
        response = test_app_client.post("/forgot-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert on_after_forgot_password_sync.called is False

    def test_not_existing_user(
        self, test_app_client: TestClient, on_after_forgot_password_sync
    ):
        json = {"email": "lancelot@camelot.bt"}
        response = test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert on_after_forgot_password_sync.called is False

    def test_inactive_user(
        self, test_app_client: TestClient, on_after_forgot_password_sync
    ):
        json = {"email": "percival@camelot.bt"}
        response = test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert on_after_forgot_password_sync.called is False

    def test_existing_user_sync_hook(
        self, test_app_client: TestClient, on_after_forgot_password_sync, user
    ):
        json = {"email": "king.arthur@camelot.bt"}
        response = test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert on_after_forgot_password_sync.called is True

        actual_user = on_after_forgot_password_sync.call_args[0][0]
        assert actual_user.id == user.id
        actual_token = on_after_forgot_password_sync.call_args[0][1]
        decoded_token = jwt.decode(
            actual_token,
            SECRET,
            audience="fastapi-users:reset",
            algorithms=[JWT_ALGORITHM],
        )
        assert decoded_token["user_id"] == user.id

    def test_existing_user_async_hook(
        self, test_app_client_async: TestClient, on_after_forgot_password_async, user
    ):
        json = {"email": "king.arthur@camelot.bt"}
        response = test_app_client_async.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert on_after_forgot_password_async.called is True

        actual_user = on_after_forgot_password_async.call_args[0][0]
        assert actual_user.id == user.id
        actual_token = on_after_forgot_password_async.call_args[0][1]
        decoded_token = jwt.decode(
            actual_token,
            SECRET,
            audience="fastapi-users:reset",
            algorithms=[JWT_ALGORITHM],
        )
        assert decoded_token["user_id"] == user.id


class TestResetPassword:
    def test_empty_body(self, test_app_client: TestClient):
        response = test_app_client.post("/reset-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_token(self, test_app_client: TestClient):
        json = {"password": "guinevere"}
        response = test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_password(self, test_app_client: TestClient):
        json = {"token": "foo"}
        response = test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_token(self, test_app_client: TestClient):
        json = {"token": "foo", "password": "guinevere"}
        response = test_app_client.post("/reset-password", json=json)
        print(response.json(), response.status_code)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_inactive_user(
        self,
        mocker,
        mock_user_db,
        test_app_client: TestClient,
        forgot_password_token,
        inactive_user: BaseUserDB,
    ):
        mocker.spy(mock_user_db, "update")

        json = {
            "token": forgot_password_token(inactive_user.id),
            "password": "holygrail",
        }
        response = test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert mock_user_db.update.called is False

    def test_existing_user(
        self,
        mocker,
        mock_user_db,
        test_app_client: TestClient,
        forgot_password_token,
        user: BaseUserDB,
    ):
        mocker.spy(mock_user_db, "update")

        json = {"token": forgot_password_token(user.id), "password": "holygrail"}
        response = test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != user.hashed_password
