import jwt
import pytest
from fastapi import Depends, FastAPI
from starlette import status
from starlette.responses import Response
from starlette.testclient import TestClient

from fastapi_users.authentication.jwt import JWTAuthentication
from fastapi_users.models import BaseUserDB
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt

SECRET = "SECRET"
LIFETIME = 3600


@pytest.fixture
def jwt_authentication():
    return JWTAuthentication(SECRET, LIFETIME)


@pytest.fixture
def token():
    def _token(user, lifetime=LIFETIME):
        data = {"user_id": user.id, "aud": "fastapi-users:auth"}
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _token


@pytest.fixture
def test_auth_client(jwt_authentication, mock_user_db):
    app = FastAPI()

    @app.get("/test-auth")
    def test_auth(
        user: BaseUserDB = Depends(jwt_authentication.get_current_user(mock_user_db))
    ):
        return user

    return TestClient(app)


@pytest.mark.asyncio
async def test_get_login_response(jwt_authentication, user):
    login_response = await jwt_authentication.get_login_response(user, Response())

    assert "token" in login_response

    token = login_response["token"]
    decoded = jwt.decode(
        token, SECRET, audience="fastapi-users:auth", algorithms=[JWT_ALGORITHM]
    )
    assert decoded["user_id"] == user.id


class TestGetCurrentUser:
    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get("/test-auth")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get(
            "/test-auth", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, token, inactive_user):
        response = test_auth_client.get(
            "/test-auth", headers={"Authorization": f"Bearer {token(inactive_user)}"}
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == inactive_user.id

    def test_valid_token(self, test_auth_client, token, user):
        response = test_auth_client.get(
            "/test-auth", headers={"Authorization": f"Bearer {token(user)}"}
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == user.id
