import uuid
from typing import Optional, Type

import pydantic
from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    """Base User model."""

    id: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    @pydantic.validator("id", pre=True, always=True)
    def default_id(cls, v):
        return v or str(uuid.uuid4())

    def create_update_dict(self):
        return self.dict(
            exclude_unset=True, exclude={"id", "is_superuser", "is_active"}
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class BaseUserCreate(BaseUser):
    email: EmailStr
    password: str


class BaseUserUpdate(BaseUser):
    password: Optional[str]


class BaseUserDB(BaseUser):
    hashed_password: str


class Models:
    """Generate models inheriting from the custom User model."""

    def __init__(self, user_model: Type[BaseUser]):
        class UserCreate(user_model, BaseUserCreate):  # type: ignore
            pass

        class UserUpdate(user_model, BaseUserUpdate):  # type: ignore
            pass

        class UserDB(user_model, BaseUserDB):  # type: ignore
            pass

        self.User = user_model
        self.UserCreate = UserCreate
        self.UserUpdate = UserUpdate
        self.UserDB = UserDB
