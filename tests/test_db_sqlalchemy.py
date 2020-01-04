import sqlite3
from typing import AsyncGenerator

import pytest
import sqlalchemy
from databases import Database
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from fastapi_users.db.sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users.password import get_password_hash
from tests.conftest import UserDB


@pytest.fixture
async def sqlalchemy_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    Base: DeclarativeMeta = declarative_base()

    class User(SQLAlchemyBaseUserTable, Base):
        first_name = Column(String, nullable=True)

    DATABASE_URL = "sqlite:///./test.db"
    database = Database(DATABASE_URL)

    engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    await database.connect()

    yield SQLAlchemyUserDatabase(UserDB, database, User.__table__)

    Base.metadata.drop_all(engine)


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries(sqlalchemy_user_db: SQLAlchemyUserDatabase[UserDB]):
    user = UserDB(
        id="111",
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
    )

    # Create
    user_db = await sqlalchemy_user_db.create(user)
    assert user_db.id is not None
    assert user_db.is_active is True
    assert user_db.is_superuser is False
    assert user_db.email == user.email

    # Update
    user_db.is_superuser = True
    await sqlalchemy_user_db.update(user_db)

    # Get by id
    id_user = await sqlalchemy_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user_db.id
    assert id_user.is_superuser is True

    # Get by email
    email_user = await sqlalchemy_user_db.get_by_email(str(user.email))
    assert email_user is not None
    assert email_user.id == user_db.id

    # List
    users = await sqlalchemy_user_db.list()
    assert len(users) == 1
    first_user = users[0]
    assert first_user.id == user_db.id

    # Exception when inserting existing email
    with pytest.raises(sqlite3.IntegrityError):
        await sqlalchemy_user_db.create(user)

    # Exception when inserting non-nullable fields
    with pytest.raises(sqlite3.IntegrityError):
        wrong_user = UserDB(id="222", hashed_password="aaa")
        await sqlalchemy_user_db.create(wrong_user)

    # Unknown user
    unknown_user = await sqlalchemy_user_db.get_by_email("galahad@camelot.bt")
    assert unknown_user is None

    # Delete user
    await sqlalchemy_user_db.delete(user)
    deleted_user = await sqlalchemy_user_db.get(user.id)
    assert deleted_user is None


@pytest.mark.asyncio
@pytest.mark.db
async def test_queries_custom_fields(
    sqlalchemy_user_db: SQLAlchemyUserDatabase[UserDB],
):
    """It should output custom fields in query result."""
    user = UserDB(
        id="111",
        email="lancelot@camelot.bt",
        hashed_password=get_password_hash("guinevere"),
        first_name="Lancelot",
    )
    await sqlalchemy_user_db.create(user)

    id_user = await sqlalchemy_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.first_name == user.first_name
