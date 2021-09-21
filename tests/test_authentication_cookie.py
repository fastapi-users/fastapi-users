import re

import pytest
from fastapi import Response

from fastapi_users.authentication.cookie import CookieAuthentication
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt

LIFETIME = 3600
COOKIE_NAME = "COOKIE_NAME"


@pytest.fixture(
    params=[
        ("/", None, True, True),
        ("/arthur", None, True, True),
        ("/", "camelot.bt", True, True),
        ("/", None, False, True),
        ("/", None, True, False),
    ]
)
def cookie_authentication(secret: SecretType, request):
    path, domain, secure, httponly = request.param
    return CookieAuthentication(
        secret,
        lifetime_seconds=LIFETIME,
        cookie_name=COOKIE_NAME,
        cookie_path=path,
        cookie_domain=domain,
        cookie_secure=secure,
        cookie_httponly=httponly,
    )


@pytest.fixture
def token(secret):
    def _token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(data, secret, lifetime)

    return _token


@pytest.mark.authentication
def test_default_name(cookie_authentication: CookieAuthentication):
    assert cookie_authentication.name == "cookie"


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_missing_token(
        self, user_manager, cookie_authentication: CookieAuthentication
    ):
        authenticated_user = await cookie_authentication(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self, user_manager, cookie_authentication: CookieAuthentication
    ):
        authenticated_user = await cookie_authentication("foo", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(
        self, user_manager, token, cookie_authentication: CookieAuthentication
    ):
        authenticated_user = await cookie_authentication(token(), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(
        self, user_manager, token, cookie_authentication: CookieAuthentication
    ):
        authenticated_user = await cookie_authentication(token("foo"), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self, user_manager, token, cookie_authentication: CookieAuthentication
    ):
        authenticated_user = await cookie_authentication(
            token("d35d213e-f3d8-4f08-954a-7e0d1bea286f"), user_manager
        )
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self, user_manager, token, user, cookie_authentication: CookieAuthentication
    ):
        authenticated_user = await cookie_authentication(token(user.id), user_manager)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(
    user, cookie_authentication: CookieAuthentication, user_manager
):
    secret = cookie_authentication.secret
    path = cookie_authentication.cookie_path
    domain = cookie_authentication.cookie_domain
    secure = cookie_authentication.cookie_secure
    httponly = cookie_authentication.cookie_httponly

    response = Response()
    login_response = await cookie_authentication.get_login_response(
        user, response, user_manager
    )

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
    assert cookie_name_value is not None

    cookie_name = cookie_name_value[1]
    assert cookie_name == COOKIE_NAME

    cookie_value = cookie_name_value[2]
    decoded = decode_jwt(cookie_value, secret, audience=["fastapi-users:auth"])
    assert decoded["user_id"] == str(user.id)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(
    user, cookie_authentication: CookieAuthentication, user_manager
):
    response = Response()
    logout_response = await cookie_authentication.get_logout_response(
        user, response, user_manager
    )

    # We shouldn't return directly the response
    # so that FastAPI can terminate it properly
    assert logout_response is None

    cookies = [header for header in response.raw_headers if header[0] == b"set-cookie"]
    assert len(cookies) == 1

    cookie = cookies[0][1].decode("latin-1")

    assert "Max-Age=0" in cookie
