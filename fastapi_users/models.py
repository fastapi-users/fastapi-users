import uuid
from typing import List, Optional, TypeVar

from pydantic import UUID4, BaseModel, EmailStr, Field


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class BaseUser(CreateUpdateDictModel):
    """Base User model."""

    id: UUID4 = Field(default_factory=uuid.uuid4)
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class BaseUserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class BaseUserUpdate(CreateUpdateDictModel):
    password: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_verified: Optional[bool]


class BaseUserDB(BaseUser):
    hashed_password: str

    class Config:
        orm_mode = True


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)
UD = TypeVar("UD", bound=BaseUserDB)


class BaseOAuthAccount(BaseModel):
    """Base OAuth account model."""

    id: UUID4 = Field(default_factory=uuid.uuid4)
    oauth_name: str
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str

    class Config:
        orm_mode = True


class BaseOAuthAccountMixin(BaseModel):
    """Adds OAuth accounts list to a User model."""

    oauth_accounts: List[BaseOAuthAccount] = []
