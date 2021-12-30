import os

import motor.motor_asyncio
from fastapi_users.db import MongoDBUserDatabase

from app.models import UserDB

DATABASE_URL = os.environ["DATABASE_URL"]
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["database_name"]
collection = db["users"]


async def get_user_db():
    yield MongoDBUserDatabase(UserDB, collection)
