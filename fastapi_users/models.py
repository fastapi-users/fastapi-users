import uuid
from typing import List, Optional, TypeVar

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
            exclude_unset=True,
            exclude={"id", "is_superuser", "is_active", "oauth_accounts"},
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class BaseUserCreate(BaseUser):
    email: EmailStr
    password: str


class BaseUserUpdate(BaseUser):
    password: Optional[str]


class BaseUserDB(BaseUser):
    id: str
    hashed_password: str

    class Config:
        orm_mode = True


UD = TypeVar("UD", bound=BaseUserDB)


class BaseOAuthAccount(BaseModel):
    """Base OAuth account model."""

    id: Optional[str] = None
    oauth_name: str
    access_token: str
    expires_at: int
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str

    @pydantic.validator("id", pre=True, always=True)
    def default_id(cls, v):
        return v or str(uuid.uuid4())

    class Config:
        orm_mode = True


class BaseOAuthAccountMixin(BaseModel):
    """Adds OAuth accounts list to a User model."""

    oauth_accounts: List[BaseOAuthAccount] = []
