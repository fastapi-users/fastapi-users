import motor.motor_asyncio
from fastapi_users.db import MongoDBUserDatabase
from fastapi_users_db_mongodb.access_token import MongoDBAccessTokenDatabase

from .models import AccessToken, UserDB

DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["database_name"]
users_collection = db["users"]
access_tokens_collection = db["access_tokens"]


async def get_user_db():
    yield MongoDBUserDatabase(UserDB, users_collection)


async def get_access_token_db():
    yield MongoDBAccessTokenDatabase(AccessToken, access_tokens_collection)
