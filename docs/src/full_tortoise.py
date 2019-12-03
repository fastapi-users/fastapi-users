from fastapi import FastAPI
from fastapi_users import BaseUser, FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db.tortoise import BaseUserModel, TortoiseUserDatabase
from tortoise import Model
from tortoise.contrib.starlette import register_tortoise

DATABASE_URL = "sqlite://./test.db"
SECRET = "SECRET"


class UserModel(BaseUserModel, Model):
    pass


class User(BaseUser):
    pass


auth = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)
user_db = TortoiseUserDatabase(UserModel)
app = FastAPI()

register_tortoise(app, db_url=DATABASE_URL, modules={"models": ["test"]})
fastapi_users = FastAPIUsers(user_db, auth, User, SECRET)
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])


@fastapi_users.on_after_register()
def on_after_register(user: User):
    print(f"User {user.id} has registered.")


@fastapi_users.on_after_forgot_password()
def on_after_forgot_password(user: User, token: str):
    print(f"User {user.id} has forgot their password. Reset token: {token}")
