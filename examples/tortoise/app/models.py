from fastapi_users import models, schemas
from fastapi_users.db import TortoiseBaseUserModel
from tortoise.contrib.pydantic import PydanticModel


class User(schemas.BaseUser):
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
