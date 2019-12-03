from fastapi import FastAPI
from fastapi_users.db.tortoise import BaseUserModel, TortoiseUserDatabase
from tortoise import Model
from tortoise.contrib.starlette import register_tortoise

DATABASE_URL = "sqlite://./test.db"


class UserModel(BaseUserModel, Model):
    pass


user_db = TortoiseUserDatabase(UserModel)
app = FastAPI()

register_tortoise(app, modules={"models": ["path_to_your_package"]})
