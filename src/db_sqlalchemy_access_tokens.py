import databases
import sqlalchemy
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from .models import AccessToken, UserDB

DATABASE_URL = "sqlite:///./test.db"
database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


class AccessTokenTable(SQLAlchemyBaseAccessTokenTable, Base):
    pass


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)

users = UserTable.__table__
access_tokens = AccessTokenTable.__table__


async def get_user_db():
    yield SQLAlchemyUserDatabase(UserDB, database, users)


async def get_access_token_db():
    yield SQLAlchemyAccessTokenDatabase(AccessToken, database, access_tokens)
