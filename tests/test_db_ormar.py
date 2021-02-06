import uuid
from sqlite3 import IntegrityError
from typing import AsyncGenerator

import databases
import ormar
import pytest
import sqlalchemy
from ormar.exceptions import NoMatch

from fastapi_users.db.ormar import (
    OrmarBaseOAuthAccountModel,
    OrmarBaseUserModel,
    OrmarUserDatabase,
)
from fastapi_users.password import get_password_hash
from tests.conftest import UserDB, UserDBOAuth

DATABASE_URL = "sqlite:///./test-ormar-user.db"
metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)


class User(OrmarBaseUserModel):
    class Meta:
        metadata = metadata
        database = database

    first_name = ormar.String(nullable=True, max_length=255)


class OAuthAccount(OrmarBaseOAuthAccountModel):
    class Meta:
        metadata = metadata
        database = database

    user = ormar.ForeignKey(User, related_name="oauth_accounts")


@pytest.fixture
async def ormar_user_db() -> AsyncGenerator[OrmarUserDatabase, None]:
    engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
    metadata.create_all(engine)

    await database.connect()

    yield OrmarUserDatabase(user_db_model=UserDB, model=User)

    metadata.drop_all(engine)
    await database.disconnect()


@pytest.fixture
async def ormar_user_db_oauth() -> AsyncGenerator[OrmarUserDatabase, None]:
    engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
    metadata.create_all(engine)

    await database.connect()

    yield OrmarUserDatabase(
        user_db_model=UserDBOAuth, model=User, oauth_account_model=OAuthAccount
    )

    metadata.drop_all(engine)
    await database.disconnect()


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries(ormar_user_db: OrmarUserDatabase[UserDB]):
    user = UserDB(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
    )

    # Create
    user_db = await ormar_user_db.create(user)
    assert user_db.id is not None
    assert user_db.is_active is True
    assert user_db.is_superuser is False
    assert user_db.email == user.email

    # Update
    user_db.is_superuser = True
    await ormar_user_db.update(user_db)

    # Exception when updating a user with a not existing id
    id_backup = user_db.id
    user_db.id = uuid.uuid4()
    with pytest.raises(NoMatch):
        await ormar_user_db.update(user_db)
    user_db.id = id_backup

    # Get by id
    id_user = await ormar_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user_db.id
    assert id_user.is_superuser is True

    # Get by email
    email_user = await ormar_user_db.get_by_email(str(user.email))
    assert email_user is not None
    assert email_user.id == user_db.id

    # Get by uppercased email
    email_user = await ormar_user_db.get_by_email("Lancelot@camelot.bt")
    assert email_user is not None
    assert email_user.id == user_db.id

    # Exception when inserting existing email
    with pytest.raises(IntegrityError):
        await ormar_user_db.create(user)

    # Exception when inserting non-nullable fields
    with pytest.raises(ValueError):
        wrong_user = UserDB(hashed_password="aaa")
        await ormar_user_db.create(wrong_user)

    # Unknown user
    unknown_user = await ormar_user_db.get_by_email("galahad@camelot.bt")
    assert unknown_user is None

    # Delete user
    await ormar_user_db.delete(user)
    deleted_user = await ormar_user_db.get(user.id)
    assert deleted_user is None


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_custom_fields(ormar_user_db: OrmarUserDatabase[UserDB]):
    """It should output custom fields in query result."""
    user = UserDB(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        first_name="Lancelot",
    )
    await ormar_user_db.create(user)

    id_user = await ormar_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.first_name == user.first_name


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_oauth(
    ormar_user_db_oauth: OrmarUserDatabase[UserDBOAuth],
    oauth_account1,
    oauth_account2,
    oauth_account3,
):
    user = UserDBOAuth(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        oauth_accounts=[oauth_account1, oauth_account2],
    )

    # Create
    user_db = await ormar_user_db_oauth.create(user)
    assert user_db.id is not None
    assert hasattr(user_db, "oauth_accounts")
    assert len(user_db.oauth_accounts) == 2

    # Update
    oauth_to_check_id = user_db.oauth_accounts[0].id
    user_db.oauth_accounts[0].access_token = "NEW_TOKEN"
    await ormar_user_db_oauth.update(user_db)

    # Get by id
    id_user = await ormar_user_db_oauth.get(user.id)
    assert id_user is not None
    assert id_user.id == user_db.id
    updated_oauth = next(
        (oauth for oauth in id_user.oauth_accounts if oauth.id == oauth_to_check_id),
        None,
    )
    assert updated_oauth.access_token == "NEW_TOKEN"

    # Add new oauth
    id_user.oauth_accounts.append(oauth_account3)
    await ormar_user_db_oauth.update(id_user)
    id_user_updated = await ormar_user_db_oauth.get(user.id)
    assert len(id_user_updated.oauth_accounts) == 3

    # Remove oauth2 and update
    id_user.oauth_accounts = [
        oauth for oauth in id_user.oauth_accounts if oauth.id != oauth_account2.id
    ]
    await ormar_user_db_oauth.update(id_user)
    id_user_updated = await ormar_user_db_oauth.get(user.id)
    assert len(id_user_updated.oauth_accounts) == 2

    # Get by email
    email_user = await ormar_user_db_oauth.get_by_email(str(user.email))
    assert email_user is not None
    assert email_user.id == user_db.id
    assert len(email_user.oauth_accounts) == 2

    # Get by OAuth account
    oauth_user = await ormar_user_db_oauth.get_by_oauth_account(
        oauth_account1.oauth_name, oauth_account1.account_id
    )
    assert oauth_user is not None
    assert oauth_user.id == user.id

    # Unknown OAuth account
    unknown_oauth_user = await ormar_user_db_oauth.get_by_oauth_account("foo", "bar")
    assert unknown_oauth_user is None
