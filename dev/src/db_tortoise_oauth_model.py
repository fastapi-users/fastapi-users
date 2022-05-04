from fastapi_users import models, schemas
from fastapi_users.db import TortoiseBaseOAuthAccountModel, TortoiseBaseUserModel
from tortoise import fields
from tortoise.contrib.pydantic import PydanticModel


class User(schemas.BaseUser, schemas.BaseOAuthAccountMixin):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UserModel(TortoiseBaseUserModel):
    pass


class UserDB(User, schemas.BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = UserModel


class OAuthAccount(TortoiseBaseOAuthAccountModel):
    user = fields.ForeignKeyField("models.UserModel", related_name="oauth_accounts")
