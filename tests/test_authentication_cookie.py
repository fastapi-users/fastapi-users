import re

import jwt
import pytest
from fastapi import Response

from fastapi_users.authentication.cookie import CookieAuthentication
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt

SECRET = "SECRET"
LIFETIME = 3600
COOKIE_NAME = "COOKIE_NAME"

cookie_authentication = CookieAuthentication(SECRET, LIFETIME, COOKIE_NAME)
cookie_authentication_path = CookieAuthentication(
    SECRET, LIFETIME, COOKIE_NAME, cookie_path="/arthur"
)
cookie_authentication_domain = CookieAuthentication(
    SECRET, LIFETIME, COOKIE_NAME, cookie_domain="camelot.bt"
)
cookie_authentication_secure = CookieAuthentication(
    SECRET, LIFETIME, COOKIE_NAME, cookie_secure=False
)
cookie_authentication_httponly = CookieAuthentication(
    SECRET, LIFETIME, COOKIE_NAME, cookie_httponly=False
)


@pytest.fixture
def token():
    def _token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _token


@pytest.mark.authentication
def test_default_name():
    assert cookie_authentication.name == "cookie"


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_missing_token(self, mock_user_db):
        authenticated_user = await cookie_authentication(None, mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(self, mock_user_db):
        authenticated_user = await cookie_authentication("foo", mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(self, mock_user_db, token):
        authenticated_user = await cookie_authentication(token(), mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(self, mock_user_db, token):
        authenticated_user = await cookie_authentication(token("foo"), mock_user_db)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(self, mock_user_db, token, user):
        authenticated_user = await cookie_authentication(token(user.id), mock_user_db)
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cookie_authentication,path,domain,secure,httponly",
    [
        (cookie_authentication, "/", None, True, True),
        (cookie_authentication_path, "/arthur", None, True, True),
        (cookie_authentication_domain, "/", "camelot.bt", True, True),
        (cookie_authentication_secure, "/", None, False, True),
        (cookie_authentication_httponly, "/", None, True, False),
    ],
)
async def test_get_login_response(
    user, cookie_authentication, path, domain, secure, httponly
):
    response = Response()
    login_response = await cookie_authentication.get_login_response(user, response)

    # We shouldn't return directly the response
    # so that FastAPI can terminate it properly
    assert login_response is None

    cookies = [header for header in response.raw_headers if header[0] == b"set-cookie"]
    assert len(cookies) == 1

    cookie = cookies[0][1].decode("latin-1")

    assert f"Max-Age={LIFETIME}" in cookie
    assert f"Path={path}" in cookie

    if domain:
        assert f"Domain={domain}" in cookie
    else:
        assert "Domain=" not in cookie

    if secure:
        assert "Secure" in cookie
    else:
        assert "Secure" not in cookie

    if httponly:
        assert "HttpOnly" in cookie
    else:
        assert "HttpOnly" not in cookie

    cookie_name_value = re.match(r"^(\w+)=([^;]+);", cookie)

    cookie_name = cookie_name_value[1]
    assert cookie_name == COOKIE_NAME

    cookie_value = cookie_name_value[2]
    decoded = jwt.decode(
        cookie_value, SECRET, audience="fastapi-users:auth", algorithms=[JWT_ALGORITHM]
    )
    assert decoded["user_id"] == str(user.id)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(user):
    response = Response()
    logout_response = await cookie_authentication.get_logout_response(user, response)

    # We shouldn't return directly the response
    # so that FastAPI can terminate it properly
    assert logout_response is None

    cookies = [header for header in response.raw_headers if header[0] == b"set-cookie"]
    assert len(cookies) == 1

    cookie = cookies[0][1].decode("latin-1")

    assert "Max-Age=0" in cookie
