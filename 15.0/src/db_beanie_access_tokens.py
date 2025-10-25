import motor.motor_asyncio
from beanie import Document
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from fastapi_users_db_beanie.access_token import (
    BeanieAccessTokenDatabase,
    BeanieBaseAccessToken,
)

DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["database_name"]


class User(BeanieBaseUser, Document):
    pass


class AccessToken(BeanieBaseAccessToken, Document):  # (1)!
    pass


async def get_user_db():
    yield BeanieUserDatabase(User)


async def get_access_token_db():  # (2)!
    yield BeanieAccessTokenDatabase(AccessToken)
