from typing import Any, Awaitable, Callable, Dict, Generic, Optional, Type, Union

from pydantic.types import UUID4

try:
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore

from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users import models, password
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import get_password_hash


class FastAPIUsersException(Exception):
    pass


class UserAlreadyExists(FastAPIUsersException):
    pass


class UserNotExists(FastAPIUsersException):
    pass


class UserAlreadyVerified(FastAPIUsersException):
    pass


class InvalidPasswordException(FastAPIUsersException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason


class ValidatePasswordProtocol(Protocol):  # pragma: no cover
    def __call__(
        self, password: str, user: Union[models.BaseUserCreate, models.BaseUserDB]
    ) -> Awaitable[None]:
        pass


class UserManager(Generic[models.UD]):

    user_db_model: Type[models.UD]
    user_db: BaseUserDatabase[models.UD]
    validate_password: Optional[ValidatePasswordProtocol]

    def __init__(
        self,
        user_db_model: Type[models.UD],
        user_db: BaseUserDatabase[models.UD],
        validate_password: Optional[ValidatePasswordProtocol] = None,
    ):
        self.user_db_model = user_db_model
        self.user_db = user_db
        self.validate_password = validate_password

    async def get(self, id: UUID4) -> models.UD:
        user = await self.user_db.get(id)

        if user is None:
            raise UserNotExists()

        return user

    async def get_by_email(self, user_email: str) -> models.UD:
        user = await self.user_db.get_by_email(user_email)

        if user is None:
            raise UserNotExists()

        return user

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> models.UD:
        user = await self.user_db.get_by_oauth_account(oauth, account_id)

        if user is None:
            raise UserNotExists()

        return user

    async def create(
        self, user: models.BaseUserCreate, safe: bool = False
    ) -> models.UD:
        if self.validate_password:
            await self.validate_password(user.password, user)

        existing_user = await self.user_db.get_by_email(user.email)
        if existing_user is not None:
            raise UserAlreadyExists()

        hashed_password = get_password_hash(user.password)
        user_dict = (
            user.create_update_dict() if safe else user.create_update_dict_superuser()
        )
        db_user = self.user_db_model(**user_dict, hashed_password=hashed_password)
        return await self.user_db.create(db_user)

    async def verify(self, user: models.UD) -> models.UD:
        if user.is_verified:
            raise UserAlreadyVerified()

        user.is_verified = True
        return await self.user_db.update(user)

    async def update(
        self, updated_user: models.BaseUserUpdate, user: models.UD, safe: bool = False
    ) -> models.UD:
        if safe:
            updated_user_data = updated_user.create_update_dict()
        else:
            updated_user_data = updated_user.create_update_dict_superuser()
        return await self._update(user, updated_user_data)

    async def delete(self, user: models.UD) -> None:
        await self.user_db.delete(user)

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[models.UD]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.
        """
        try:
            user = await self.get_by_email(credentials.username)
        except UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            password.get_password_hash(credentials.password)
            return None

        verified, updated_password_hash = password.verify_and_update_password(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            user.hashed_password = updated_password_hash
            await self.user_db.update(user)

        return user

    async def _update(self, user: models.UD, update_dict: Dict[str, Any]) -> models.UD:
        for field in update_dict:
            if field == "email":
                try:
                    await self.get_by_email(update_dict[field])
                    raise UserAlreadyExists()
                except UserNotExists:
                    user.email = update_dict[field]
            elif field == "password":
                password = update_dict[field]
                if self.validate_password:
                    await self.validate_password(password, user)
                hashed_password = get_password_hash(password)
                user.hashed_password = hashed_password
            else:
                setattr(user, field, update_dict[field])
        updated_user = await self.user_db.update(user)
        return updated_user


UserManagerDependency = Callable[..., UserManager[models.UD]]
