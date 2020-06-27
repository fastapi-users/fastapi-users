import motor.motor_asyncio
from fastapi import FastAPI
from fastapi_users import models
from fastapi_users.db import MongoDBUserDatabase


class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["database_name"]
collection = db["users"]


app = FastAPI()


user_db = MongoDBUserDatabase(UserDB, collection)
