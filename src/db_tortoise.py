from fastapi import FastAPI
from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel, TortoiseUserDatabase
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import PydanticModel


class UserModel(TortoiseBaseUserModel):
    pass


class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = UserModel


DATABASE_URL = "sqlite://./test.db"

user_db = TortoiseUserDatabase(UserDB, UserModel)
app = FastAPI()

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["path_to_your_package"]},
    generate_schemas=True,
)
