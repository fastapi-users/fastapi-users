from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel
from tortoise.contrib.pydantic import PydanticModel


class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(models.BaseUserUpdate):
    pass


class UserModel(TortoiseBaseUserModel):
    pass


class UserDB(User, models.BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = UserModel
