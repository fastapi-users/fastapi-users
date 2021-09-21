import pytest
from fastapi import Response

from fastapi_users.authentication import BaseAuthentication


@pytest.fixture
def base_authentication():
    return BaseAuthentication()


@pytest.mark.authentication
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_not_implemented(self, base_authentication, user_manager):
        with pytest.raises(NotImplementedError):
            await base_authentication(None, user_manager)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_login_response(base_authentication, user, user_manager):
    with pytest.raises(NotImplementedError):
        await base_authentication.get_login_response(user, Response(), user_manager)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_get_logout_response(base_authentication, user, user_manager):
    with pytest.raises(NotImplementedError):
        await base_authentication.get_logout_response(user, Response(), user_manager)
