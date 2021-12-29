import pytest
from fastapi import Response, status

from fastapi_users.authentication.transport import BearerTransport
from fastapi_users.authentication.transport.bearer import BearerResponse


@pytest.fixture()
def bearer_transport() -> BearerTransport:
    return BearerTransport(tokenUrl="/login")


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(bearer_transport: BearerTransport):
    response = Response()
    login_response = await bearer_transport.get_login_response("TOKEN", response)

    assert isinstance(login_response, BearerResponse)

    assert login_response.access_token == "TOKEN"
    assert login_response.token_type == "bearer"


@pytest.mark.authentication
@pytest.mark.openapi
def test_get_openapi_login_responses_success(bearer_transport: BearerTransport):
    openapi_responses = bearer_transport.get_openapi_login_responses_success()
    assert openapi_responses[status.HTTP_200_OK]["model"] == BearerResponse
