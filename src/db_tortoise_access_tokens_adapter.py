from fastapi_users.db import TortoiseUserDatabase
from fastapi_users_db_tortoise.access_token import TortoiseAccessTokenDatabase

from .models import AccessToken, AccessTokenModel, UserDB, UserModel

DATABASE_URL = "sqlite://./test.db"


async def get_user_db():
    yield TortoiseUserDatabase(UserDB, UserModel)


async def get_access_token_db():
    yield TortoiseAccessTokenDatabase(AccessToken, AccessTokenModel)
