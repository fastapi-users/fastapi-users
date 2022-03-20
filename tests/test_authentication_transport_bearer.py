import pytest
from fastapi import Response, status

from fastapi_users.authentication.transport import (
    BearerTransport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.authentication.transport.bearer import BearerResponse


@pytest.fixture()
def bearer_transport(request: pytest.FixtureRequest) -> BearerTransport:
    param: str = request.param  # type: ignore
    if param == "password":
        return BearerTransport(tokenUrl="/login")
    elif param == "authorization_code":
        return BearerTransport(
            tokenUrl="/token",
            authorizationUrl="/authorize",
            grant_type="authorization_code",
        )
    else:
        raise ValueError(f"Unsupported grant type: {param}")


async def test_bad_grant_type():
    with pytest.raises(ValueError):
        BearerTransport(
            tokenUrl="/token",
            grant_type="not_implemented",
        )


@pytest.mark.parametrize(
    "bearer_transport",
    ["password", "authorization_code"],
    indirect=True,
)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(bearer_transport: BearerTransport):
    response = Response()
    login_response = await bearer_transport.get_login_response("TOKEN", response)

    assert isinstance(login_response, BearerResponse)

    assert login_response.access_token == "TOKEN"
    assert login_response.token_type == "bearer"


@pytest.mark.parametrize(
    "bearer_transport",
    ["password", "authorization_code"],
    indirect=True,
)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(bearer_transport: BearerTransport):
    response = Response()
    with pytest.raises(TransportLogoutNotSupportedError):
        await bearer_transport.get_logout_response(response)


@pytest.mark.parametrize(
    "bearer_transport",
    ["password", "authorization_code"],
    indirect=True,
)
@pytest.mark.authentication
@pytest.mark.openapi
def test_get_openapi_login_responses_success(bearer_transport: BearerTransport):
    openapi_responses = bearer_transport.get_openapi_login_responses_success()
    assert openapi_responses[status.HTTP_200_OK]["model"] == BearerResponse


@pytest.mark.parametrize(
    "bearer_transport",
    ["password", "authorization_code"],
    indirect=True,
)
@pytest.mark.authentication
@pytest.mark.openapi
def test_get_openapi_logout_responses_success(bearer_transport: BearerTransport):
    openapi_responses = bearer_transport.get_openapi_logout_responses_success()
    assert openapi_responses == {}
