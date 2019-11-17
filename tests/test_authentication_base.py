import pytest
from starlette.requests import Request

from fastapi_users.authentication import BaseAuthentication


@pytest.fixture
def base_authentication():
    return BaseAuthentication()


@pytest.mark.authentication
class TestAuthenticate:

    @pytest.mark.asyncio
    async def test_not_implemented(self, base_authentication, mock_user_db, request_builder):
        request = request_builder({})
        with pytest.raises(NotImplementedError):
            await base_authentication(request, mock_user_db)
