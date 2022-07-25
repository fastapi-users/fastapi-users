import re

import pytest
from fastapi import Response, status

from fastapi_users.authentication.transport import CookieTransport

COOKIE_MAX_AGE = 3600
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
def cookie_transport(request) -> CookieTransport:
    path, domain, secure, httponly = request.param
    return CookieTransport(
        cookie_name=COOKIE_NAME,
        cookie_max_age=COOKIE_MAX_AGE,
        cookie_path=path,
        cookie_domain=domain,
        cookie_secure=secure,
        cookie_httponly=httponly,
    )


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(cookie_transport: CookieTransport):
    path = cookie_transport.cookie_path
    domain = cookie_transport.cookie_domain
    secure = cookie_transport.cookie_secure
    httponly = cookie_transport.cookie_httponly

    response = Response()
    login_response = await cookie_transport.get_login_response("TOKEN", response)

    assert login_response is None

    cookies = [header for header in response.raw_headers if header[0] == b"set-cookie"]
    assert len(cookies) == 1

    cookie = cookies[0][1].decode("latin-1")

    assert f"Max-Age={COOKIE_MAX_AGE}" in cookie
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
    assert cookie_value == "TOKEN"


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(cookie_transport: CookieTransport):
    response = Response()
    logout_response = await cookie_transport.get_logout_response(response)

    assert logout_response is None

    cookies = [header for header in response.raw_headers if header[0] == b"set-cookie"]
    assert len(cookies) == 1

    cookie = cookies[0][1].decode("latin-1")

    assert "Max-Age=0" in cookie


@pytest.mark.authentication
@pytest.mark.openapi
def test_get_openapi_login_responses_success(cookie_transport: CookieTransport):
    assert cookie_transport.get_openapi_login_responses_success() == {
        status.HTTP_200_OK: {"model": None}
    }


@pytest.mark.authentication
@pytest.mark.openapi
def test_get_openapi_logout_responses_success(cookie_transport: CookieTransport):
    assert cookie_transport.get_openapi_logout_responses_success() == {
        status.HTTP_200_OK: {"model": None}
    }
