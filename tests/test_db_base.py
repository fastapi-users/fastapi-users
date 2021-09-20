import pytest

from fastapi_users.db import BaseUserDatabase
from tests.conftest import UserDB


@pytest.mark.asyncio
@pytest.mark.db
async def test_not_implemented_methods(user):
    base_user_db = BaseUserDatabase(UserDB)

    with pytest.raises(NotImplementedError):
        await base_user_db.get("aaa")

    with pytest.raises(NotImplementedError):
        await base_user_db.get_by_email("lancelot@camelot.bt")

    with pytest.raises(NotImplementedError):
        await base_user_db.get_by_oauth_account("google", "user_oauth1")

    with pytest.raises(NotImplementedError):
        await base_user_db.create(user)

    with pytest.raises(NotImplementedError):
        await base_user_db.update(user)

    with pytest.raises(NotImplementedError):
        await base_user_db.delete(user)
