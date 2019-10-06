import uuid
from typing import Optional

from pydantic import BaseModel
from pydantic.types import EmailStr


class UserBase(BaseModel):
    id: str = uuid.uuid4
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    pass


class UserDB(UserBase):
    hashed_password: str


class User(UserBase):
    pass
