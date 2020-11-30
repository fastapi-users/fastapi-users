from typing import Awaitable, Type

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

from fastapi_users import models
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import get_password_hash


class UserAlreadyExists(Exception):
    pass


class CreateUserProtocol(Protocol):  # pragma: no cover
    def __call__(
        self, user: models.BaseUserCreate, safe: bool = False
    ) -> Awaitable[models.BaseUserDB]:
        pass


def get_create_user(
    user_db: BaseUserDatabase[models.BaseUserDB],
    user_db_model: Type[models.BaseUserDB],
) -> CreateUserProtocol:
    async def create_user(
        user: models.BaseUserCreate, safe: bool = False
    ) -> models.BaseUserDB:
        existing_user = await user_db.get_by_email(user.email)

        if existing_user is not None:
            raise UserAlreadyExists()

        hashed_password = get_password_hash(user.password)
        user_dict = (
            user.create_update_dict() if safe else user.create_update_dict_superuser()
        )
        db_user = user_db_model(**user_dict, hashed_password=hashed_password)
        return await user_db.create(db_user)

    return create_user
