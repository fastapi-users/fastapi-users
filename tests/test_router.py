from unittest.mock import MagicMock

import asynctest
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
    def _forgot_password_token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:reset"}
        if user_id is not None:
            data["user_id"] = user_id
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _forgot_password_token


def on_after_forgot_password_sync():
    return MagicMock(return_value=None)


def on_after_forgot_password_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[on_after_forgot_password_sync, on_after_forgot_password_async])
def on_after_forgot_password(request):
    return request.param()


@pytest.fixture()
def test_app_client(
    mock_user_db, mock_authentication, on_after_forgot_password
) -> TestClient:
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

    def test_existing_user(self, test_app_client: TestClient):
        json = {"email": "king.arthur@camelot.bt", "password": "guinevere"}
        response = test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_valid_body(self, test_app_client: TestClient):
        json = {"email": "lancelot@camelot.bt", "password": "guinevere"}
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
    def test_empty_body(self, test_app_client: TestClient, on_after_forgot_password):
        response = test_app_client.post("/forgot-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert on_after_forgot_password.called is False

    def test_not_existing_user(
        self, test_app_client: TestClient, on_after_forgot_password
    ):
        json = {"email": "lancelot@camelot.bt"}
        response = test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert on_after_forgot_password.called is False

    def test_inactive_user(self, test_app_client: TestClient, on_after_forgot_password):
        json = {"email": "percival@camelot.bt"}
        response = test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert on_after_forgot_password.called is False

    def test_existing_user(
        self, test_app_client: TestClient, on_after_forgot_password, user
    ):
        json = {"email": "king.arthur@camelot.bt"}
        response = test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert on_after_forgot_password.called is True

        actual_user = on_after_forgot_password.call_args[0][0]
        assert actual_user.id == user.id
        actual_token = on_after_forgot_password.call_args[0][1]
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

    def test_valid_token_missing_user_id_payload(
        self,
        mocker,
        mock_user_db,
        test_app_client: TestClient,
        forgot_password_token,
        inactive_user: BaseUserDB,
    ):
        mocker.spy(mock_user_db, "update")

        json = {"token": forgot_password_token(), "password": "holygrail"}
        response = test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert mock_user_db.update.called is False

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
        current_hashed_passord = user.hashed_password

        json = {"token": forgot_password_token(user.id), "password": "holygrail"}
        response = test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_passord
