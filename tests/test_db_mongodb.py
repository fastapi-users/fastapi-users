from typing import AsyncGenerator

import motor.motor_asyncio
import pytest
import pymongo.errors

from fastapi_users.db.mongodb import MongoDBUserDatabase
from fastapi_users.password import get_password_hash
from tests.conftest import UserDB


@pytest.fixture
async def mongodb_user_db() -> AsyncGenerator[MongoDBUserDatabase, None]:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://localhost:27017", serverSelectionTimeoutMS=100
    )

    try:
        await client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        pytest.skip("MongoDB not available", allow_module_level=True)
        return

    db = client["test_database"]
    collection = db["users"]

    yield MongoDBUserDatabase(UserDB, collection)

    await collection.drop()


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries(mongodb_user_db: MongoDBUserDatabase[UserDB]):
    user = UserDB(
        id="111",
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
    )

    # Create
    user_db = await mongodb_user_db.create(user)
    assert user_db.id is not None
    assert user_db.is_active is True
    assert user_db.is_superuser is False
    assert user_db.email == user.email

    # Update
    user_db.is_superuser = True
    await mongodb_user_db.update(user_db)

    # Get by id
    id_user = await mongodb_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user_db.id
    assert id_user.is_superuser is True

    # Get by email
    email_user = await mongodb_user_db.get_by_email(str(user.email))
    assert email_user is not None
    assert email_user.id == user_db.id

    # List
    users = await mongodb_user_db.list()
    assert len(users) == 1
    first_user = users[0]
    assert first_user.id == user_db.id

    # Exception when inserting existing email
    with pytest.raises(pymongo.errors.DuplicateKeyError):
        await mongodb_user_db.create(user)

    # Unknown user
    unknown_user = await mongodb_user_db.get_by_email("galahad@camelot.bt")
    assert unknown_user is None

    # Delete user
    await mongodb_user_db.delete(user)
    deleted_user = await mongodb_user_db.get(user.id)
    assert deleted_user is None


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_custom_fields(mongodb_user_db: MongoDBUserDatabase[UserDB]):
    """It should output custom fields in query result."""
    user = UserDB(
        id="111",
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        first_name="Lancelot",
    )
    await mongodb_user_db.create(user)

    id_user = await mongodb_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.first_name == user.first_name
