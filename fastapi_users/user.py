from typing import Awaitable, Type

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

from pydantic import EmailStr

from fastapi_users import models
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import get_password_hash


class UserAlreadyExists(Exception):
    pass


class UserNotExists(Exception):
    pass


class UserAlreadyVerified(Exception):
    pass


class CreateUserProtocol(Protocol):  # pragma: no cover
    def __call__(
        self,
        user: models.BaseUserCreate,
        safe: bool = False,
        is_active: bool = None,
        is_verified: bool = None,
    ) -> Awaitable[models.BaseUserDB]:
        pass


def get_create_user(
    user_db: BaseUserDatabase[models.BaseUserDB],
    user_db_model: Type[models.BaseUserDB],
) -> CreateUserProtocol:
    async def create_user(
        user: models.BaseUserCreate,
        safe: bool = False,
        is_active: bool = None,
        is_verified: bool = None,
    ) -> models.BaseUserDB:
        existing_user = await user_db.get_by_email(user.email)

        if existing_user is not None and existing_user.is_active:
            raise UserAlreadyExists()

        hashed_password = get_password_hash(user.password)
        user_dict = (
            user.create_update_dict() if safe else user.create_update_dict_superuser()
        )
        if is_active is not None:
            user_dict["is_active"] = is_active
        if is_verified is not None:
            user_dict["is_verified"] = is_verified
        db_user = user_db_model(**user_dict, hashed_password=hashed_password)
        return await user_db.create(db_user)

    return create_user


class VerifyUserProtocol(Protocol):
    def __call__(self, user_uuid: str) -> Awaitable[models.BaseUserDB]:
        pass


def get_verify_user(
    user_db: BaseUserDatabase[models.BaseUserDB],
) -> VerifyUserProtocol:
    async def verify_user(user_uuid: str) -> models.BaseUserDB:
        user = await user_db.get(user_uuid)

        if user is None:
            raise UserNotExists()

        if user.is_verified:
            raise UserAlreadyVerified()

        user.is_verified = True
        return await user_db.update(user)

    return verify_user


class GetUserProtocol(Protocol):
    def __call__(self, user_uuid: str) -> Awaitable[models.BaseUserDB]:
        pass


def get_get_user(
    user_db: BaseUserDatabase[models.BaseUserDB],
) -> GetUserProtocol:
    async def get_user(user_email: EmailStr) -> models.BaseUserDB:
        if not (user_email == EmailStr(user_email)):
            raise UserNotExists()

        user = await user_db.get_by_email(user_email)

        if user is None:
            raise UserNotExists()

        return user

    return get_user
