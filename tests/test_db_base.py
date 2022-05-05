import uuid

import pytest

from fastapi_users.db import BaseUserDatabase
from tests.conftest import IDType, OAuthAccountModel, UserModel


@pytest.mark.asyncio
@pytest.mark.db
async def test_not_implemented_methods(
    user: UserModel, oauth_account1: OAuthAccountModel
):
    base_user_db = BaseUserDatabase[UserModel, IDType]()

    with pytest.raises(NotImplementedError):
        await base_user_db.get(uuid.uuid4())

    with pytest.raises(NotImplementedError):
        await base_user_db.get_by_email("lancelot@camelot.bt")

    with pytest.raises(NotImplementedError):
        await base_user_db.get_by_oauth_account("google", "user_oauth1")

    with pytest.raises(NotImplementedError):
        await base_user_db.create({})

    with pytest.raises(NotImplementedError):
        await base_user_db.update(user, {})

    with pytest.raises(NotImplementedError):
        await base_user_db.delete(user)

    with pytest.raises(NotImplementedError):
        await base_user_db.add_oauth_account(user, {})

    with pytest.raises(NotImplementedError):
        await base_user_db.update_oauth_account(user, oauth_account1, {})
