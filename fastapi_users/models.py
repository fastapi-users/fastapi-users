import uuid
from typing import List, Optional, TypeVar

from pydantic import Field, UUID4, BaseModel, EmailStr


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
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class BaseUserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class BaseUserUpdate(BaseUser):
    password: Optional[str]


class BaseUserDB(BaseUser):
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
    hashed_password: str

    class Config:
        orm_mode = True


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
