from typing import AsyncGenerator

import motor.motor_asyncio
import pytest
import pymongo.errors

from fastapi_users.db.mongodb import MongoDBUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.password import get_password_hash


@pytest.fixture
async def mongodb_user_db() -> AsyncGenerator[MongoDBUserDatabase, None]:
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    collection = db["users"]

    yield MongoDBUserDatabase(collection)

    await collection.drop()


@pytest.mark.asyncio
async def test_queries(mongodb_user_db):
    user = BaseUserDB(
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
    assert id_user.id == user_db.id
    assert id_user.is_superuser is True

    # Get by email
    email_user = await mongodb_user_db.get_by_email(user.email)
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
