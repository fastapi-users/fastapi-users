from fastapi import FastAPI
from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel, TortoiseUserDatabase
from tortoise.contrib.fastapi import register_tortoise


class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


DATABASE_URL = "sqlite://./test.db"


class UserModel(TortoiseBaseUserModel):
    pass


user_db = TortoiseUserDatabase(UserDB, UserModel)
app = FastAPI()

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["path_to_your_package"]},
    generate_schemas=True,
)
