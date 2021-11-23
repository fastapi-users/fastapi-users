import pytest
from fastapi import Response

from fastapi_users.authentication.jwt import JWTAuthentication
from fastapi_users.jwt import decode_jwt, generate_jwt

LIFETIME = 3600
TOKEN_URL = "/login"


@pytest.fixture
def jwt_authentication(secret):
    return JWTAuthentication(secret, LIFETIME, TOKEN_URL)


@pytest.fixture
def token(secret):
    def _token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(data, secret, lifetime)

    return _token


@pytest.mark.authentication
def test_default_name(jwt_authentication):
    assert jwt_authentication.name == "jwt"


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_missing_token(self, jwt_authentication, user_manager):
        authenticated_user = await jwt_authentication(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(self, jwt_authentication, user_manager):
        authenticated_user = await jwt_authentication("foo", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(
        self, jwt_authentication, user_manager, token
    ):
        authenticated_user = await jwt_authentication(token(), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(
        self, jwt_authentication, user_manager, token
    ):
        authenticated_user = await jwt_authentication(token("foo"), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self, jwt_authentication, user_manager, token
    ):
        authenticated_user = await jwt_authentication(
            token("d35d213e-f3d8-4f08-954a-7e0d1bea286f"), user_manager
        )
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(self, jwt_authentication, mock_user_db, token, user):
        authenticated_user = await jwt_authentication(token(user.id), mock_user_db)
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(jwt_authentication, user, user_manager):
    login_response = await jwt_authentication.get_login_response(
        user, Response(), user_manager
    )

    assert login_response.token_type == "bearer"

    decoded = decode_jwt(
        login_response.access_token,
        jwt_authentication.secret,
        audience=["fastapi-users:auth"],
    )
    assert decoded["user_id"] == str(user.id)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(jwt_authentication, user, user_manager):
    with pytest.raises(NotImplementedError):
        await jwt_authentication.get_logout_response(user, Response(), user_manager)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response_success(jwt_authentication, user, user_manager):
    with pytest.raises(NotImplementedError):
        await jwt_authentication.get_openapi_logout_responses_success()
