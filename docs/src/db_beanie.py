from beanie import Document
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from pymongo import AsyncMongoClient

DATABASE_URL = "mongodb://localhost:27017"
client = AsyncMongoClient(DATABASE_URL, uuidRepresentation="standard")
db = client["database_name"]


class User(BeanieBaseUser, Document):
    pass


async def get_user_db():
    yield BeanieUserDatabase(User)
