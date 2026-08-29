from beanie import Document
from fastapi_users.db import BaseOAuthAccount, BeanieBaseUser, BeanieUserDatabase
from pydantic import Field
from pymongo import AsyncMongoClient

DATABASE_URL = "mongodb://localhost:27017"
client = AsyncMongoClient(DATABASE_URL, uuidRepresentation="standard")
db = client["database_name"]


class OAuthAccount(BaseOAuthAccount):
    pass


class User(BeanieBaseUser, Document):
    oauth_accounts: list[OAuthAccount] = Field(default_factory=list)


async def get_user_db():
    yield BeanieUserDatabase(User, OAuthAccount)
