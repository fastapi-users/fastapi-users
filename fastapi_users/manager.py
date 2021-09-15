from typing import Any, Callable, Dict, Generic, Optional, Type, Union

import jwt
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4

from fastapi_users import models, password
from fastapi_users.db import BaseUserDatabase
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.password import generate_password, get_password_hash

RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"


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


class InvalidVerifyToken(FastAPIUsersException):
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

    verification_token_secret: SecretType
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = VERIFY_USER_TOKEN_AUDIENCE

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

    async def oauth_callback(
        self, oauth_account: models.BaseOAuthAccount, request: Optional[Request] = None
    ) -> models.UD:
        try:
            user = await self.get_by_oauth_account(
                oauth_account.oauth_name, oauth_account.account_id
            )
        except UserNotExists:
            try:
                # Link account
                user = await self.get_by_email(oauth_account.account_email)
                user.oauth_accounts.append(oauth_account)  # type: ignore
                await self.user_db.update(user)
            except UserNotExists:
                # Create account
                password = generate_password()
                user = self.user_db_model(
                    email=oauth_account.account_email,
                    hashed_password=get_password_hash(password),
                    oauth_accounts=[oauth_account],
                )
                await self.user_db.create(user)
                await self.on_after_register(user, request)
        else:
            # Update oauth
            updated_oauth_accounts = []
            for existing_oauth_account in user.oauth_accounts:  # type: ignore
                if existing_oauth_account.account_id == oauth_account.account_id:
                    updated_oauth_accounts.append(oauth_account)
                else:
                    updated_oauth_accounts.append(existing_oauth_account)
            user.oauth_accounts = updated_oauth_accounts  # type: ignore
            await self.user_db.update(user)

        return user

    async def request_verify(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise UserInactive()
        if user.is_verified:
            raise UserAlreadyVerified()

        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )
        await self.on_after_request_verify(user, token, request)

    async def verify(self, token: str, request: Optional[Request] = None) -> models.UD:
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise InvalidVerifyToken()

        try:
            user_id = data["user_id"]
            email = data["email"]
        except KeyError:
            raise InvalidVerifyToken()

        try:
            user = await self.get_by_email(email)
        except UserNotExists:
            raise InvalidVerifyToken()

        try:
            user_uuid = UUID4(user_id)
        except ValueError:
            raise InvalidVerifyToken()

        if user_uuid != user.id:
            raise InvalidVerifyToken()

        if user.is_verified:
            raise UserAlreadyVerified()

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)

        return verified_user

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

    async def update(
        self,
        user_update: models.UU,
        user: models.UD,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UD:
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()
        updated_user = await self._update(user, updated_user_data)
        await self.on_after_update(updated_user, updated_user_data, request)
        return updated_user

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

    async def on_after_update(
        self,
        user: models.UD,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        return  # pragma: no cover

    async def on_after_request_verify(
        self, user: models.UD, token: str, request: Optional[Request] = None
    ) -> None:
        return  # pragma: no cover

    async def on_after_verify(
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
