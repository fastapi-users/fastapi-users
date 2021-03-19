from typing import AsyncGenerator

import pymongo.errors
import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi_users.db.mongodb import MongoDBUserDatabase
from fastapi_users.password import get_password_hash
from tests.conftest import UserDB, UserDBOAuth


@pytest.fixture(scope="module")
async def mongodb_client():
    client = AsyncIOMotorClient(
        "mongodb://localhost:27017",
        serverSelectionTimeoutMS=100,
        uuidRepresentation="standard",
    )

    try:
        await client.server_info()
        yield client
        client.close()
    except pymongo.errors.ServerSelectionTimeoutError:
        pytest.skip("MongoDB not available", allow_module_level=True)
        return


@pytest.fixture
def get_mongodb_user_db(mongodb_client: AsyncIOMotorClient):
    async def _get_mongodb_user_db(
        user_model,
    ) -> AsyncGenerator[MongoDBUserDatabase, None]:
        db = mongodb_client["test_database"]
        collection = db["users"]

        yield MongoDBUserDatabase(user_model, collection)

        await collection.delete_many({})

    return _get_mongodb_user_db


@pytest.fixture
async def mongodb_user_db(get_mongodb_user_db):
    async for u in get_mongodb_user_db(UserDB):
        yield u


@pytest.fixture
async def mongodb_user_db_oauth(get_mongodb_user_db):
    async for u in get_mongodb_user_db(UserDBOAuth):
        yield u


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries(mongodb_user_db: MongoDBUserDatabase[UserDB]):
    user = UserDB(
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

    # Get by uppercased email
    email_user = await mongodb_user_db.get_by_email("Lancelot@camelot.bt")
    assert email_user is not None
    assert email_user.id == user_db.id

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
@pytest.mark.parametrize(
    "email,query,found",
    [
        ("lancelot@camelot.bt", "lancelot@camelot.bt", True),
        ("lancelot@camelot.bt", "LanceloT@camelot.bt", True),
        ("lancelot@camelot.bt", "lancelot.@camelot.bt", False),
        ("lancelot@camelot.bt", "lancelot.*", False),
        ("lancelot@camelot.bt", "lancelot+guinevere@camelot.bt", False),
        ("lancelot+guinevere@camelot.bt", "lancelot+guinevere@camelot.bt", True),
        ("lancelot+guinevere@camelot.bt", "lancelot.*", False),
        ("квіточка@пошта.укр", "квіточка@пошта.укр", True),
        ("квіточка@пошта.укр", "КВІТОЧКА@ПОШТА.УКР", True),
    ],
)
async def test_email_query(
    mongodb_user_db: MongoDBUserDatabase[UserDB], email: str, query: str, found: bool
):
    user = UserDB(
        email=email,
        hashed_password=get_password_hash("guinevere"),
    )
    await mongodb_user_db.create(user)

    email_user = await mongodb_user_db.get_by_email(query)

    if found:
        assert email_user is not None
        assert email_user.id == user.id
    else:
        assert email_user is None


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_custom_fields(mongodb_user_db: MongoDBUserDatabase[UserDB]):
    """It should output custom fields in query result."""
    user = UserDB(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        first_name="Lancelot",
    )
    await mongodb_user_db.create(user)

    id_user = await mongodb_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.first_name == user.first_name


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_oauth(
    mongodb_user_db_oauth: MongoDBUserDatabase[UserDBOAuth],
    oauth_account1,
    oauth_account2,
):
    user = UserDBOAuth(
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        oauth_accounts=[oauth_account1, oauth_account2],
    )

    # Create
    user_db = await mongodb_user_db_oauth.create(user)
    assert user_db.id is not None
    assert hasattr(user_db, "oauth_accounts")
    assert len(user_db.oauth_accounts) == 2

    # Update
    user_db.oauth_accounts[0].access_token = "NEW_TOKEN"
    await mongodb_user_db_oauth.update(user_db)

    # Get by id
    id_user = await mongodb_user_db_oauth.get(user.id)
    assert id_user is not None
    assert id_user.id == user_db.id
    assert id_user.oauth_accounts[0].access_token == "NEW_TOKEN"

    # Get by email
    email_user = await mongodb_user_db_oauth.get_by_email(str(user.email))
    assert email_user is not None
    assert email_user.id == user_db.id
    assert len(email_user.oauth_accounts) == 2

    # Get by OAuth account
    oauth_user = await mongodb_user_db_oauth.get_by_oauth_account(
        oauth_account1.oauth_name, oauth_account1.account_id
    )
    assert oauth_user is not None
    assert oauth_user.id == user.id

    # Unknown OAuth account
    unknown_oauth_user = await mongodb_user_db_oauth.get_by_oauth_account("foo", "bar")
    assert unknown_oauth_user is None
