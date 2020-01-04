import re

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
def test_default_name(cookie_authentication):
    assert cookie_authentication.name == "cookie"


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
    response = Response()
    login_response = await cookie_authentication.get_login_response(user, response)

    # We shouldn't return directly the response
    # so that FastAPI can terminate it properly
    assert login_response is None

    cookies = [header for header in response.raw_headers if header[0] == b"set-cookie"]
    assert len(cookies) == 1

    cookie = cookies[0][1].decode("latin-1")

    assert f"Max-Age={LIFETIME}" in cookie

    cookie_name_value = re.match(r"^(\w+)=([^;]+);", cookie)

    cookie_name = cookie_name_value[1]
    assert cookie_name == COOKIE_NAME

    cookie_value = cookie_name_value[2]
    decoded = jwt.decode(
        cookie_value, SECRET, audience="fastapi-users:auth", algorithms=[JWT_ALGORITHM]
    )
    assert decoded["user_id"] == user.id
