from typing import Callable, Sequence, Type

from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.router import Event, UserRouter, get_user_router


class FastAPIUsers:
    """
    Main object that ties together the component for users authentication.

    :param db: Database adapter instance.
    :param auth_backends: List of authentication backends.
    :param user_model: Pydantic model of a user.
    :param user_create_model: Pydantic model for creating a user.
    :param user_update_model: Pydantic model for updating a user.
    :param user_db_model: Pydantic model of a DB representation of a user.
    :param reset_password_token_secret: Secret to encode reset password token.
    :param reset_password_token_lifetime_seconds: Lifetime of reset password token.

    :attribute router: Router exposing authentication routes.
    :attribute get_current_user: Dependency callable to inject authenticated user.
    """

    db: BaseUserDatabase
    authenticator: Authenticator
    router: UserRouter

    def __init__(
        self,
        db: BaseUserDatabase,
        auth_backends: Sequence[BaseAuthentication],
        user_model: Type[models.BaseUser],
        user_create_model: Type[models.BaseUserCreate],
        user_update_model: Type[models.BaseUserUpdate],
        user_db_model: Type[models.BaseUserDB],
        reset_password_token_secret: str,
        reset_password_token_lifetime_seconds: int = 3600,
    ):
        self.db = db
        self.authenticator = Authenticator(auth_backends, db)
        self.router = get_user_router(
            self.db,
            user_model,
            user_create_model,
            user_update_model,
            user_db_model,
            self.authenticator,
            reset_password_token_secret,
            reset_password_token_lifetime_seconds,
        )

        self.get_current_user = self.authenticator.get_current_user
        self.get_current_active_user = self.authenticator.get_current_active_user
        self.get_current_superuser = self.authenticator.get_current_superuser

    def on_after_register(self) -> Callable:
        """Add an event handler on successful registration."""
        return self._on_event(Event.ON_AFTER_REGISTER)

    def on_after_forgot_password(self) -> Callable:
        """Add an event handler on successful forgot password request."""
        return self._on_event(Event.ON_AFTER_FORGOT_PASSWORD)

    def _on_event(self, event_type: Event) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.router.add_event_handler(event_type, func)
            return func

        return decorator
