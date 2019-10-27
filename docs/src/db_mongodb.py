import motor.motor_asyncio
from fastapi import FastAPI
from fastapi_users.db import MongoDBUserDatabase

DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client["database_name"]
collection = db["users"]


app = FastAPI()


user_db = MongoDBUserDatabase(collection)
