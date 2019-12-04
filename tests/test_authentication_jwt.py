import jwt
import pytest
from starlette.responses import Response

from fastapi_users.authentication.jwt import JWTAuthentication
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt

SECRET = "SECRET"
LIFETIME = 3600
TOKEN_URL = "/login"


@pytest.fixture
def jwt_authentication():
    return JWTAuthentication(SECRET, LIFETIME, TOKEN_URL)


@pytest.fixture
def token():
    def _token(user=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user is not None:
            data["user_id"] = user.id
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _token


@pytest.mark.authentication
def test_default_name(jwt_authentication):
    assert jwt_authentication.name == "jwt"


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_missing_token(
        self, jwt_authentication, mock_user_db, request_builder
    ):
        request = request_builder(headers={})
        authenticated_user = await jwt_authentication(request, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self, jwt_authentication, mock_user_db, request_builder
    ):
        request = request_builder(headers={"Authorization": "Bearer foo"})
        authenticated_user = await jwt_authentication(request, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(
        self, jwt_authentication, mock_user_db, request_builder, token
    ):
        request = request_builder(headers={"Authorization": f"Bearer {token()}"})
        authenticated_user = await jwt_authentication(request, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self, jwt_authentication, mock_user_db, request_builder, token, user
    ):
        request = request_builder(headers={"Authorization": f"Bearer {token(user)}"})
        authenticated_user = await jwt_authentication(request, mock_user_db)
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(jwt_authentication, user):
    login_response = await jwt_authentication.get_login_response(user, Response())

    assert "token" in login_response

    token = login_response["token"]
    decoded = jwt.decode(
        token, SECRET, audience="fastapi-users:auth", algorithms=[JWT_ALGORITHM]
    )
    assert decoded["user_id"] == user.id
