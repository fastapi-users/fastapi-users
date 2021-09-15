from typing import Any, Callable, Dict, Generic, Optional, Type, Union

import jwt
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4

from fastapi_users import models, password
from fastapi_users.db import BaseUserDatabase
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.password import get_password_hash

RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"


class FastAPIUsersException(Exception):
    pass


class UserAlreadyExists(FastAPIUsersException):
    pass


class UserNotExists(FastAPIUsersException):
    pass


class UserInactive(FastAPIUsersException):
    pass


class UserAlreadyVerified(FastAPIUsersException):
    pass


class InvalidResetPasswordToken(FastAPIUsersException):
    pass


class InvalidPasswordException(FastAPIUsersException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason


class BaseUserManager(Generic[models.UC, models.UD]):

    user_db_model: Type[models.UD]
    user_db: BaseUserDatabase[models.UD]

    reset_password_token_secret: SecretType
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = RESET_PASSWORD_TOKEN_AUDIENCE

    def __init__(
        self,
        user_db_model: Type[models.UD],
        user_db: BaseUserDatabase[models.UD],
    ):
        self.user_db_model = user_db_model
        self.user_db = user_db

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
        self, user: models.UC, safe: bool = False, request: Optional[Request] = None
    ) -> models.UD:
        await self.validate_password(user.password, user)

        existing_user = await self.user_db.get_by_email(user.email)
        if existing_user is not None:
            raise UserAlreadyExists()

        hashed_password = get_password_hash(user.password)
        user_dict = (
            user.create_update_dict() if safe else user.create_update_dict_superuser()
        )
        db_user = self.user_db_model(**user_dict, hashed_password=hashed_password)

        created_user = await self.user_db.create(db_user)

        await self.on_after_register(created_user, request)

        return created_user

    async def forgot_password(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise UserInactive()

        token_data = {"user_id": str(user.id), "aud": RESET_PASSWORD_TOKEN_AUDIENCE}
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
        self, token: str, password: str, request: Optional[Request] = None
    ) -> models.UD:
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise InvalidResetPasswordToken()

        try:
            user_id = data["user_id"]
        except KeyError:
            raise InvalidResetPasswordToken()

        try:
            user_uuid = UUID4(user_id)
        except ValueError:
            raise InvalidResetPasswordToken()

        user = await self.get(user_uuid)

        if not user.is_active:
            raise UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def verify(self, user: models.UD) -> models.UD:
        if user.is_verified:
            raise UserAlreadyVerified()

        user.is_verified = True
        return await self.user_db.update(user)

    async def update(
        self, updated_user: models.UU, user: models.UD, safe: bool = False
    ) -> models.UD:
        if safe:
            updated_user_data = updated_user.create_update_dict()
        else:
            updated_user_data = updated_user.create_update_dict_superuser()
        return await self._update(user, updated_user_data)

    async def delete(self, user: models.UD) -> None:
        await self.user_db.delete(user)

    async def validate_password(
        self, password: str, user: Union[models.UC, models.UD]
    ) -> None:
        return  # pragma: no cover

    async def on_after_register(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        return  # pragma: no cover

    async def on_after_forgot_password(
        self, user: models.UD, token: str, request: Optional[Request] = None
    ) -> None:
        return  # pragma: no cover

    async def on_after_reset_password(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        return  # pragma: no cover

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
                await self.validate_password(password, user)
                hashed_password = get_password_hash(password)
                user.hashed_password = hashed_password
            else:
                setattr(user, field, update_dict[field])
        updated_user = await self.user_db.update(user)
        return updated_user


UserManagerDependency = Callable[..., BaseUserManager[models.UC, models.UD]]
