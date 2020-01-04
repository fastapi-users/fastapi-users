from typing import AsyncGenerator

import pytest
from tortoise.exceptions import IntegrityError
from tortoise import Tortoise, fields

from fastapi_users.db.tortoise import TortoiseUserDatabase, TortoiseBaseUserModel
from fastapi_users.password import get_password_hash
from tests.conftest import UserDB


class User(TortoiseBaseUserModel):
    first_name = fields.CharField(null=True, max_length=255)


@pytest.fixture
async def tortoise_user_db() -> AsyncGenerator[TortoiseUserDatabase, None]:
    DATABASE_URL = "sqlite://./test.db"

    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": ["tests.test_db_tortoise"]}
    )
    await Tortoise.generate_schemas()

    yield TortoiseUserDatabase(UserDB, User)

    await User.all().delete()
    await Tortoise.close_connections()


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries(tortoise_user_db: TortoiseUserDatabase[UserDB]):
    user = UserDB(
        id="111",
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

    # List
    users = await tortoise_user_db.list()
    assert len(users) == 1
    first_user = users[0]
    assert first_user.id == user_db.id

    # Exception when inserting existing email
    with pytest.raises(IntegrityError):
        await tortoise_user_db.create(user)

    # Exception when inserting non-nullable fields
    with pytest.raises(ValueError):
        wrong_user = UserDB(id="222", hashed_password="aaa")
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
        id="111",
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        first_name="Lancelot",
    )
    await tortoise_user_db.create(user)

    id_user = await tortoise_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.first_name == user.first_name
