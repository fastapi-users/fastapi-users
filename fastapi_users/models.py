import uuid
from typing import Optional

import pydantic
from pydantic import BaseModel
from pydantic.types import EmailStr


class UserBase(BaseModel):
    id: str = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    @pydantic.validator("id", pre=True, always=True)
    def default_id(cls, v):
        return v or str(uuid.uuid4())


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    pass


class UserDB(UserBase):
    hashed_password: str


class User(UserBase):
    pass
