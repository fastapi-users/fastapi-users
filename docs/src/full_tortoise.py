from fastapi import FastAPI
from tortoise import Model
from fastapi_users import BaseUser, FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from tortoise.contrib.starlette import register_tortoise
from fastapi_users.db.tortoise import BaseUserModel, TortoiseUserDatabase

DATABASE_URL = "sqlite://./test.db"
SECRET = "SECRET"

class User(BaseUserModel, Model):
    pass

class UserPydantic(BaseUser):
    pass

auth = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)
user_db = TortoiseUserDatabase(User)
app = FastAPI()

register_tortoise(app, db_url=DATABASE_URL, modules={"models": ["test"]})
fastapi_users = FastAPIUsers(user_db, auth, UserPydantic, SECRET)
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])


@fastapi_users.on_after_register()
def on_after_register(user: UserPydantic):
    print(f"User {user.id} has registered.")


@fastapi_users.on_after_forgot_password()
def on_after_forgot_password(user: UserPydantic, token: str):
    print(f"User {user.id} has forgot their password. Reset token: {token}")
