import motor.motor_asyncio
from fastapi import FastAPI
from fastapi_users import BaseUser, FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import MongoDBUserDatabase

DATABASE_URL = "mongodb://localhost:27017"
SECRET = "SECRET"


client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client["database_name"]
collection = db["users"]


user_db = MongoDBUserDatabase(collection)


class User(BaseUser):
    pass


auth_backends = [
    JWTAuthentication(secret=SECRET, lifetime_seconds=3600),
]

app = FastAPI()
fastapi_users = FastAPIUsers(user_db, auth_backends, User, SECRET)
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])


@fastapi_users.on_after_register()
def on_after_register(user: User):
    print(f"User {user.id} has registered.")


@fastapi_users.on_after_forgot_password()
def on_after_forgot_password(user: User, token: str):
    print(f"User {user.id} has forgot their password. Reset token: {token}")
