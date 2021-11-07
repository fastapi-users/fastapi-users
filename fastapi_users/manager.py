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
    """
    User management logic.

    :attribute user_db_model: Pydantic model of a DB representation of a user.
    :attribute reset_password_token_secret: Secret to encode reset password token.
    :attribute reset_password_token_lifetime_seconds: Lifetime of reset password token.
    :attribute reset_password_token_audience: JWT audience of reset password token.
    :attribute verification_token_secret: Secret to encode verification token.
    :attribute verification_token_lifetime_seconds: Lifetime of verification token.
    :attribute verification_token_audience: JWT audience of verification token.

    :param user_db: Database adapter instance.
    """

    user_db_model: Type[models.UD]
    reset_password_token_secret: SecretType
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = RESET_PASSWORD_TOKEN_AUDIENCE

    verification_token_secret: SecretType
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = VERIFY_USER_TOKEN_AUDIENCE

    user_db: BaseUserDatabase[models.UD]

    def __init__(self, user_db: BaseUserDatabase[models.UD]):
        self.user_db = user_db

    async def get(self, id: UUID4) -> models.UD:
        """
        Get a user by id.

        :param id: Id. of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get(id)

        if user is None:
            raise UserNotExists()

        return user

    async def get_by_email(self, user_email: str) -> models.UD:
        """
        Get a user by e-mail.

        :param user_email: E-mail of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_email(user_email)

        if user is None:
            raise UserNotExists()

        return user

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> models.UD:
        """
        Get a user by OAuth account.

        :param oauth: Name of the OAuth client.
        :param account_id: Id. of the account on the external OAuth service.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_oauth_account(oauth, account_id)

        if user is None:
            raise UserNotExists()

        return user

    async def create(
        self, user: models.UC, safe: bool = False, request: Optional[Request] = None
    ) -> models.UD:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
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
        """
        Handle the callback after a successful OAuth authentication.

        If the user already exists with this OAuth account, the token is updated.

        If a user with the same e-mail already exists,
        the OAuth account is linked to it.

        If the user does not exist, it is created and the on_after_register handler
        is triggered.

        :param oauth_account: The new OAuth account to create.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :return: A user.
        """
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
        """
        Start a verification request.

        Triggers the on_after_request_verify handler on success.

        :param user: The user to verify.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        :raises UserAlreadyVerified: The user is already verified.
        """
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
        """
        Validate a verification request.

        Changes the is_verified flag of the user to True.

        Triggers the on_after_verify handler on success.

        :param token: The verification token generated by request_verify.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises InvalidVerifyToken: The token is invalid or expired.
        :raises UserAlreadyVerified: The user is already verified.
        :return: The verified user.
        """
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
        """
        Start a forgot password request.

        Triggers the on_after_forgot_password handler on success.

        :param user: The user that forgot its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        """
        if not user.is_active:
            raise UserInactive()

        token_data = {
            "user_id": str(user.id),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
        self, token: str, password: str, request: Optional[Request] = None
    ) -> models.UD:
        """
        Reset the password of a user.

        Triggers the on_after_reset_password handler on success.

        :param token: The token generated by forgot_password.
        :param password: The new password to set.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises InvalidResetPasswordToken: The token is invalid or expired.
        :raises UserInactive: The user is inactive.
        :raises InvalidPasswordException: The password is invalid.
        :return: The user with updated password.
        """
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
        """
        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdate model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the update, defaults to False
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :return: The updated user.
        """
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()
        updated_user = await self._update(user, updated_user_data)
        await self.on_after_update(updated_user, updated_user_data, request)
        return updated_user

    async def delete(self, user: models.UD) -> None:
        """
        Delete a user.

        :param user: The user to delete.
        """
        await self.user_db.delete(user)

    async def validate_password(
        self, password: str, user: Union[models.UC, models.UD]
    ) -> None:
        """
        Validate a password.

        *You should overload this method to add your own validation logic.*

        :param password: The password to validate.
        :param user: The user associated to this password.
        :raises InvalidPasswordException: The password is invalid.
        :return: None if the password is valid.
        """
        return  # pragma: no cover

    async def on_after_register(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        """
        Perform logic after successful user registration.

        *You should overload this method to add your own logic.*

        :param user: The registered user
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_update(
        self,
        user: models.UD,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic after successful user update.

        *You should overload this method to add your own logic.*

        :param user: The updated user
        :param update_dict: Dictionary with the updated user fields.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_request_verify(
        self, user: models.UD, token: str, request: Optional[Request] = None
    ) -> None:
        """
        Perform logic after successful verification request.

        *You should overload this method to add your own logic.*

        :param user: The user to verify.
        :param token: The verification token.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_verify(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        """
        Perform logic after successful user verification.

        *You should overload this method to add your own logic.*

        :param user: The verified user.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_forgot_password(
        self, user: models.UD, token: str, request: Optional[Request] = None
    ) -> None:
        """
        Perform logic after successful forgot password request.

        *You should overload this method to add your own logic.*

        :param user: The user that forgot its password.
        :param token: The forgot password token.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_reset_password(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        """
        Perform logic after successful password reset.

        *You should overload this method to add your own logic.*

        :param user: The user that reset its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[models.UD]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
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
        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    raise UserAlreadyExists()
                except UserNotExists:
                    user.email = value
                    user.is_verified = False
            elif field == "password":
                await self.validate_password(value, user)
                hashed_password = get_password_hash(value)
                user.hashed_password = hashed_password
            else:
                setattr(user, field, value)
        return await self.user_db.update(user)


UserManagerDependency = Callable[..., BaseUserManager[models.UC, models.UD]]
