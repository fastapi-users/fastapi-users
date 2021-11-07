import databases
import sqlalchemy
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from .models import UserDB

DATABASE_URL = "sqlite:///./test.db"
database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)

users = UserTable.__table__


async def get_user_db():
    yield SQLAlchemyUserDatabase(UserDB, database, users)
