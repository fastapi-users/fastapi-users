import jwt
import pytest
from starlette.responses import Response

from fastapi_users.authentication.cookie import CookieAuthentication
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt

SECRET = "SECRET"
LIFETIME = 3600
COOKIE_NAME = "COOKIE_NAME"


@pytest.fixture
def cookie_authentication():
    return CookieAuthentication(SECRET, LIFETIME, COOKIE_NAME)


@pytest.fixture
def token():
    def _token(user=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user is not None:
            data["user_id"] = user.id
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _token


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_missing_token(
        self, cookie_authentication, mock_user_db, request_builder
    ):
        request = request_builder()
        authenticated_user = await cookie_authentication(request, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self, cookie_authentication, mock_user_db, request_builder
    ):
        cookies = {}
        cookies[COOKIE_NAME] = "foo"
        request = request_builder(cookies=cookies)
        authenticated_user = await cookie_authentication(request, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(
        self, cookie_authentication, mock_user_db, request_builder, token
    ):
        cookies = {}
        cookies[COOKIE_NAME] = token()
        request = request_builder(cookies=cookies)
        authenticated_user = await cookie_authentication(request, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self, cookie_authentication, mock_user_db, request_builder, token, user
    ):
        cookies = {}
        cookies[COOKIE_NAME] = token(user)
        request = request_builder(cookies=cookies)
        authenticated_user = await cookie_authentication(request, mock_user_db)
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(cookie_authentication, user):
    login_response = await cookie_authentication.get_login_response(user, Response())
