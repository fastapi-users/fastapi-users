from fastapi_users import models
from fastapi_users.authentication.strategy.db.models import BaseAccessToken
from fastapi_users.db import TortoiseBaseUserModel
from fastapi_users_db_tortoise.access_token import TortoiseBaseAccessTokenModel
from tortoise import fields
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


class AccessTokenModel(TortoiseBaseAccessTokenModel):
    user = fields.ForeignKeyField("models.UserModel", related_name="access_tokens")


class AccessToken(BaseAccessToken, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = AccessTokenModel
