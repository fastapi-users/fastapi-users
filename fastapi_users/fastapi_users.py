from typing import Any, Callable, Dict, Optional, Sequence, Type

from fastapi import APIRouter, Request

from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.router import (
    get_auth_router,
    get_register_router,
    get_reset_password_router,
    get_users_router,
    get_verify_router,
)
from fastapi_users.user import (
    CreateUserProtocol,
    GetUserProtocol,
    ValidatePasswordProtocol,
    VerifyUserProtocol,
    get_create_user,
    get_get_user,
    get_verify_user,
)

try:
    from httpx_oauth.oauth2 import BaseOAuth2

    from fastapi_users.router import get_oauth_router
except ModuleNotFoundError:  # pragma: no cover
    BaseOAuth2 = Type  # type: ignore


class FastAPIUsers:
    """
    Main object that ties together the component for users authentication.

    :param db: Database adapter instance.
    :param auth_backends: List of authentication backends.
    :param user_model: Pydantic model of a user.
    :param user_create_model: Pydantic model for creating a user.
    :param user_update_model: Pydantic model for updating a user.
    :param user_db_model: Pydantic model of a DB representation of a user.
    :param validate_password: Optional function to validate the password
    at user registration, user update or password reset.

    :attribute create_user: Helper function to create a user programmatically.
    :attribute current_user: Dependency callable getter to inject authenticated user
    with a specific set of parameters.
    :attribute get_current_user: Dependency callable to inject authenticated user.
    :attribute get_current_active_user: Dependency callable to inject active user.
    :attribute get_current_verified_user: Dependency callable to inject verified user.
    :attribute get_current_superuser: Dependency callable to inject superuser.
    :attribute get_current_verified_superuser: Dependency callable to inject
    verified superuser.
    """

    db: BaseUserDatabase
    authenticator: Authenticator
    create_user: CreateUserProtocol
    verify_user: VerifyUserProtocol
    get_user: GetUserProtocol
    validate_password: Optional[ValidatePasswordProtocol]
    _user_model: Type[models.BaseUser]
    _user_create_model: Type[models.BaseUserCreate]
    _user_update_model: Type[models.BaseUserUpdate]
    _user_db_model: Type[models.BaseUserDB]

    def __init__(
        self,
        db: BaseUserDatabase,
        auth_backends: Sequence[BaseAuthentication],
        user_model: Type[models.BaseUser],
        user_create_model: Type[models.BaseUserCreate],
        user_update_model: Type[models.BaseUserUpdate],
        user_db_model: Type[models.BaseUserDB],
        validate_password: Optional[ValidatePasswordProtocol] = None,
    ):
        self.db = db
        self.authenticator = Authenticator(auth_backends, db)

        self._user_model = user_model
        self._user_db_model = user_db_model
        self._user_create_model = user_create_model
        self._user_update_model = user_update_model
        self._user_db_model = user_db_model

        self.create_user = get_create_user(db, user_db_model)
        self.verify_user = get_verify_user(db)
        self.get_user = get_get_user(db)

        self.validate_password = validate_password

        self.current_user = self.authenticator.current_user
        self.get_current_user = self.authenticator.get_current_user
        self.get_current_active_user = self.authenticator.get_current_active_user
        self.get_current_verified_user = self.authenticator.get_current_verified_user
        self.get_current_superuser = self.authenticator.get_current_superuser
        self.get_current_verified_superuser = (
            self.authenticator.get_current_verified_superuser
        )
        self.get_optional_current_user = self.authenticator.get_optional_current_user
        self.get_optional_current_active_user = (
            self.authenticator.get_optional_current_active_user
        )
        self.get_optional_current_verified_user = (
            self.authenticator.get_optional_current_verified_user
        )
        self.get_optional_current_superuser = (
            self.authenticator.get_optional_current_superuser
        )
        self.get_optional_current_verified_superuser = (
            self.authenticator.get_optional_current_verified_superuser
        )

    def get_register_router(
        self,
        after_register: Optional[Callable[[models.UD, Request], None]] = None,
    ) -> APIRouter:
        """
        Return a router with a register route.

        :param after_register: Optional function called
        after a successful registration.
        """
        return get_register_router(
            self.create_user,
            self._user_model,
            self._user_create_model,
            after_register,
            self.validate_password,
        )

    def get_verify_router(
        self,
        verification_token_secret: str,
        verification_token_lifetime_seconds: int = 3600,
        after_verification_request: Optional[
            Callable[[models.UD, str, Request], None]
        ] = None,
        after_verification: Optional[Callable[[models.UD, Request], None]] = None,
    ) -> APIRouter:
        """
        Return a router with e-mail verification routes.

        :param verification_token_secret: Secret to encode verification token.
        :param verification_token_lifetime_seconds: Lifetime verification token.
        :param after_verification_request: Optional function called after a successful
        verify request.
        :param after_verification: Optional function called after a successful
        verification.
        """
        return get_verify_router(
            self.verify_user,
            self.get_user,
            self._user_model,
            verification_token_secret,
            verification_token_lifetime_seconds,
            after_verification_request,
            after_verification,
        )

    def get_reset_password_router(
        self,
        reset_password_token_secret: str,
        reset_password_token_lifetime_seconds: int = 3600,
        after_forgot_password: Optional[
            Callable[[models.UD, str, Request], None]
        ] = None,
        after_reset_password: Optional[Callable[[models.UD, Request], None]] = None,
    ) -> APIRouter:
        """
        Return a reset password process router.

        :param reset_password_token_secret: Secret to encode reset password token.
        :param reset_password_token_lifetime_seconds: Lifetime of reset password token.
        :param after_forgot_password: Optional function called after a successful
        forgot password request.
        :param after_reset_password: Optional function called after a successful
        password reset.
        """
        return get_reset_password_router(
            self.db,
            reset_password_token_secret,
            reset_password_token_lifetime_seconds,
            after_forgot_password,
            after_reset_password,
            self.validate_password,
        )

    def get_auth_router(
        self, backend: BaseAuthentication, requires_verification: bool = False
    ) -> APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param backend: The authentication backend instance.
        :param requires_verification: Whether the authentication
        require the user to be verified or not.
        """
        return get_auth_router(
            backend,
            self.db,
            self.authenticator,
            requires_verification,
        )

    def get_oauth_router(
        self,
        oauth_client: BaseOAuth2,
        state_secret: str,
        redirect_url: str = None,
        after_register: Optional[Callable[[models.UD, Request], None]] = None,
    ) -> APIRouter:
        """
        Return an OAuth router for a given OAuth client.

        :param oauth_client: The HTTPX OAuth client instance.
        :param state_secret: Secret used to encode the state JWT.
        :param redirect_url: Optional arbitrary redirect URL for the OAuth2 flow.
        If not given, the URL to the callback endpoint will be generated.
        :param after_register: Optional function called
        after a successful registration.
        """
        return get_oauth_router(
            oauth_client,
            self.db,
            self._user_db_model,
            self.authenticator,
            state_secret,
            redirect_url,
            after_register,
        )

    def get_users_router(
        self,
        after_update: Optional[
            Callable[[models.UD, Dict[str, Any], Request], None]
        ] = None,
        requires_verification: bool = False,
    ) -> APIRouter:
        """
        Return a router with routes to manage users.

        :param after_update: Optional function called
        after a successful user update.
        :param requires_verification: Whether the endpoints
        require the users to be verified or not.
        """
        return get_users_router(
            self.db,
            self._user_model,
            self._user_update_model,
            self._user_db_model,
            self.authenticator,
            after_update,
            requires_verification,
            self.validate_password,
        )
