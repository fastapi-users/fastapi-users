from typing import AsyncGenerator

import pytest
from tortoise import Tortoise, fields
from tortoise.contrib.pydantic import PydanticModel
from tortoise.exceptions import IntegrityError

from fastapi_users.db.tortoise import (
    TortoiseBaseOAuthAccountModel,
    TortoiseBaseUserModel,
    TortoiseUserDatabase,
)
from fastapi_users.password import get_password_hash
from tests.conftest import UserDB as BaseUserDB
from tests.conftest import UserDBOAuth as BaseUserDBOAuth


class User(TortoiseBaseUserModel):
    first_name = fields.CharField(null=True, max_length=255)


class UserDB(BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = User


class OAuthAccount(TortoiseBaseOAuthAccountModel):
    user = fields.ForeignKeyField("models.User", related_name="oauth_accounts")


class UserDBOAuth(BaseUserDBOAuth, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = OAuthAccount


@pytest.fixture
async def tortoise_user_db() -> AsyncGenerator[TortoiseUserDatabase, None]:
    DATABASE_URL = "sqlite://./test-tortoise-user.db"

    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": ["tests.test_db_tortoise"]}
    )
    await Tortoise.generate_schemas()

    yield TortoiseUserDatabase(UserDB, User)

    await User.all().delete()
    await Tortoise.close_connections()


@pytest.fixture
async def tortoise_user_db_oauth() -> AsyncGenerator[TortoiseUserDatabase, None]:
    DATABASE_URL = "sqlite://./test-tortoise-user-oauth.db"

    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": ["tests.test_db_tortoise"]}
    )
    await Tortoise.generate_schemas()

    yield TortoiseUserDatabase(UserDBOAuth, User, OAuthAccount)

    await User.all().delete()
    await Tortoise.close_connections()


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries(tortoise_user_db: TortoiseUserDatabase[UserDB]):
    user = UserDB(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
    )

    # Create
    user_db = await tortoise_user_db.create(user)
    assert user_db.id is not None
    assert user_db.is_active is True
    assert user_db.is_superuser is False
    assert user_db.email == user.email

    # Update
    user_db.is_superuser = True
    await tortoise_user_db.update(user_db)

    # Get by id
    id_user = await tortoise_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user_db.id
    assert id_user.is_superuser is True

    # Get by email
    email_user = await tortoise_user_db.get_by_email(str(user.email))
    assert email_user is not None
    assert email_user.id == user_db.id

    # Get by uppercased email
    email_user = await tortoise_user_db.get_by_email("Lancelot@camelot.bt")
    assert email_user is not None
    assert email_user.id == user_db.id

    # Exception when inserting existing email
    with pytest.raises(IntegrityError):
        await tortoise_user_db.create(user)

    # Exception when inserting non-nullable fields
    with pytest.raises(ValueError):
        wrong_user = UserDB(hashed_password="aaa")
        await tortoise_user_db.create(wrong_user)

    # Unknown user
    unknown_user = await tortoise_user_db.get_by_email("galahad@camelot.bt")
    assert unknown_user is None

    # Delete user
    await tortoise_user_db.delete(user)
    deleted_user = await tortoise_user_db.get(user.id)
    assert deleted_user is None


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_custom_fields(tortoise_user_db: TortoiseUserDatabase[UserDB]):
    """It should output custom fields in query result."""
    user = UserDB(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        first_name="Lancelot",
    )
    await tortoise_user_db.create(user)

    id_user = await tortoise_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.first_name == user.first_name


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_oauth(
    tortoise_user_db_oauth: TortoiseUserDatabase[UserDBOAuth],
    oauth_account1,
    oauth_account2,
):
    user = UserDBOAuth(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        oauth_accounts=[oauth_account1, oauth_account2],
    )

    # Create
    user_db = await tortoise_user_db_oauth.create(user)
    assert user_db.id is not None
    assert hasattr(user_db, "oauth_accounts")
    assert len(user_db.oauth_accounts) == 2

    # Update
    user_db.oauth_accounts[0].access_token = "NEW_TOKEN"
    await tortoise_user_db_oauth.update(user_db)

    # Get by id
    id_user = await tortoise_user_db_oauth.get(user.id)
    assert id_user is not None
    assert id_user.id == user_db.id
    assert id_user.oauth_accounts[0].access_token == "NEW_TOKEN"

    # Get by email
    email_user = await tortoise_user_db_oauth.get_by_email(str(user.email))
    assert email_user is not None
    assert email_user.id == user_db.id
    assert len(email_user.oauth_accounts) == 2

    # Get by OAuth account
    oauth_user = await tortoise_user_db_oauth.get_by_oauth_account(
        oauth_account1.oauth_name, oauth_account1.account_id
    )
    assert oauth_user is not None
    assert oauth_user.id == user.id

    # Unknown OAuth account
    unknown_oauth_user = await tortoise_user_db_oauth.get_by_oauth_account("foo", "bar")
    assert unknown_oauth_user is None
