import databases
import sqlalchemy
from fastapi_users.db import OrmarBaseUserModel, OrmarUserDatabase

from .models import UserDB

DATABASE_URL = "sqlite:///test.db"
metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)


class UserModel(OrmarBaseUserModel):
    class Meta:
        tablename = "users"
        metadata = metadata
        database = database


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


async def get_user_db():
    yield OrmarUserDatabase(UserDB, UserModel)
