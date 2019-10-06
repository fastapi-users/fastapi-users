from databases import Database
import pytest
import sqlalchemy
import sqlite3

from fastapi_users.db.sqlalchemy import Base, SQLAlchemyUserDB
from fastapi_users.models import UserDB


@pytest.fixture
async def sqlalchemy_user_db() -> SQLAlchemyUserDB:
    DATABASE_URL = 'sqlite:///./test.db'
    database = Database(DATABASE_URL)

    engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args={'check_same_thread': False}
    )
    Base.metadata.create_all(engine)

    await database.connect()

    yield SQLAlchemyUserDB(database)

    Base.metadata.drop_all(engine)


@pytest.fixture
def user() -> UserDB:
    return UserDB(
        email='king.arthur@camelot.bt',
        hashed_password='abc',
    )


@pytest.mark.asyncio
async def test_queries(user, sqlalchemy_user_db):
    # Create
    user_db = await sqlalchemy_user_db.create(user)
    assert user_db.id is not None
    assert user_db.is_active is True
    assert user_db.is_superuser is False
    assert user_db.email == user.email

    # List
    users = await sqlalchemy_user_db.list()
    assert len(users) == 1
    first_user = users[0]
    assert first_user.id == user_db.id

    # Get by email
    email_user = await sqlalchemy_user_db.get_by_email(user.email)
    assert email_user.id == user_db.id

    # Exception on existing email
    with pytest.raises(sqlite3.IntegrityError):
        await sqlalchemy_user_db.create(user)
