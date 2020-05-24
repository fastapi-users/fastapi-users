import pytest
from fastapi import Response

from fastapi_users.authentication import BaseAuthentication


@pytest.fixture
def base_authentication():
    return BaseAuthentication()


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_not_implemented(self, base_authentication, mock_user_db):
        with pytest.raises(NotImplementedError):
            await base_authentication(None, mock_user_db)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(base_authentication, user):
    with pytest.raises(NotImplementedError):
        await base_authentication.get_login_response(user, Response())


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(base_authentication, user):
    with pytest.raises(NotImplementedError):
        await base_authentication.get_logout_response(user, Response())
