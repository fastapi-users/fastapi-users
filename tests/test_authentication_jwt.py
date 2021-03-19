import jwt
import pytest
from fastapi import Response

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
    def _token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(data, SECRET, lifetime, JWT_ALGORITHM)

    return _token


@pytest.mark.authentication
def test_default_name(jwt_authentication):
    assert jwt_authentication.name == "jwt"


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_missing_token(self, jwt_authentication, mock_user_db):
        authenticated_user = await jwt_authentication(None, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(self, jwt_authentication, mock_user_db):
        authenticated_user = await jwt_authentication("foo", mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(
        self, jwt_authentication, mock_user_db, token
    ):
        authenticated_user = await jwt_authentication(token(), mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(
        self, jwt_authentication, mock_user_db, token
    ):
        authenticated_user = await jwt_authentication(token("foo"), mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(self, jwt_authentication, mock_user_db, token, user):
        authenticated_user = await jwt_authentication(token(user.id), mock_user_db)
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(jwt_authentication, user):
    login_response = await jwt_authentication.get_login_response(user, Response())

    assert "access_token" in login_response
    assert login_response["token_type"] == "bearer"

    token = login_response["access_token"]
    decoded = jwt.decode(
        token, SECRET, audience="fastapi-users:auth", algorithms=[JWT_ALGORITHM]
    )
    assert decoded["user_id"] == str(user.id)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(jwt_authentication, user):
    with pytest.raises(NotImplementedError):
        await jwt_authentication.get_logout_response(user, Response())
