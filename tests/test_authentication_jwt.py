import jwt
import pytest
from starlette import status
from starlette.responses import Response

from fastapi_users.authentication.jwt import JWTAuthentication
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt

SECRET = "SECRET"
LIFETIME = 3600


@pytest.fixture
def jwt_authentication():
    return JWTAuthentication(SECRET, LIFETIME)


@pytest.fixture
def token():
    def _token(user=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user is not None:
            data["user_id"] = user.id
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _token


@pytest.fixture
def test_auth_client(get_test_auth_client, jwt_authentication):
    return get_test_auth_client(jwt_authentication)


@pytest.mark.asyncio
async def test_get_login_response(jwt_authentication, user):
    login_response = await jwt_authentication.get_login_response(user, Response())

    assert "token" in login_response

    token = login_response["token"]
    decoded = jwt.decode(
        token, SECRET, audience="fastapi-users:auth", algorithms=[JWT_ALGORITHM]
    )
    assert decoded["user_id"] == user.id


@pytest.mark.authentication
class TestGetCurrentUser:
    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get("/test-current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get(
            "/test-current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_missing_user_payload(self, test_auth_client, token):
        response = test_auth_client.get(
            "/test-current-user", headers={"Authorization": f"Bearer {token()}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, token, inactive_user):
        response = test_auth_client.get(
            "/test-current-user",
            headers={"Authorization": f"Bearer {token(inactive_user)}"},
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == inactive_user.id

    def test_valid_token(self, test_auth_client, token, user):
        response = test_auth_client.get(
            "/test-current-user", headers={"Authorization": f"Bearer {token(user)}"}
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == user.id


@pytest.mark.authentication
class TestGetCurrentActiveUser:
    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get("/test-current-active-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get(
            "/test-current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, token, inactive_user):
        response = test_auth_client.get(
            "/test-current-active-user",
            headers={"Authorization": f"Bearer {token(inactive_user)}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token(self, test_auth_client, token, user):
        response = test_auth_client.get(
            "/test-current-active-user",
            headers={"Authorization": f"Bearer {token(user)}"},
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == user.id


@pytest.mark.authentication
class TestGetCurrentSuperuser:
    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get("/test-current-superuser")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get(
            "/test-current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, token, inactive_user):
        response = test_auth_client.get(
            "/test-current-superuser",
            headers={"Authorization": f"Bearer {token(inactive_user)}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_regular_user(self, test_auth_client, token, user):
        response = test_auth_client.get(
            "/test-current-superuser",
            headers={"Authorization": f"Bearer {token(user)}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_valid_token_superuser(self, test_auth_client, token, superuser):
        response = test_auth_client.get(
            "/test-current-superuser",
            headers={"Authorization": f"Bearer {token(superuser)}"},
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == superuser.id
