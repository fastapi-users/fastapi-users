from fastapi_users.db import TortoiseUserDatabase

from app.models import OAuthAccount, UserDB, UserModel

DATABASE_URL = "sqlite://./test.db"


async def get_user_db():
    yield TortoiseUserDatabase(UserDB, UserModel, OAuthAccount)
