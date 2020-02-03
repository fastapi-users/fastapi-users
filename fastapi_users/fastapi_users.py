from collections import defaultdict
from typing import Callable, DefaultDict, List, Sequence, Type

from httpx_oauth.oauth2 import BaseOAuth2

from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.router import (
    Event,
    EventHandlersRouter,
    get_oauth_router,
    get_user_router,
)


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
    :attribute oauth_routers: List of OAuth routers created through `get_oauth_router`.
    :attribute get_current_user: Dependency callable to inject authenticated user.
    """

    db: BaseUserDatabase
    authenticator: Authenticator
    router: EventHandlersRouter
    oauth_routers: List[EventHandlersRouter]
    _user_db_model: Type[models.BaseUserDB]
    _event_handlers: DefaultDict[Event, List[Callable]]

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
        self.oauth_routers = []
        self._user_db_model = user_db_model
        self._event_handlers = defaultdict(list)

        self.get_current_user = self.authenticator.get_current_user
        self.get_current_active_user = self.authenticator.get_current_active_user
        self.get_current_superuser = self.authenticator.get_current_superuser

    def on_after_register(self) -> Callable:
        """Add an event handler on successful registration."""
        return self._on_event(Event.ON_AFTER_REGISTER)

    def on_after_forgot_password(self) -> Callable:
        """Add an event handler on successful forgot password request."""
        return self._on_event(Event.ON_AFTER_FORGOT_PASSWORD)

    def on_after_update(self) -> Callable:
        """Add an event handler on successful update user request."""
        return self._on_event(Event.ON_AFTER_UPDATE)

    def get_oauth_router(
        self, oauth_client: BaseOAuth2, state_secret: str, redirect_url: str = None
    ) -> EventHandlersRouter:
        """
        Return an OAuth router for a given OAuth client.

        :param oauth_client: The HTTPX OAuth client instance.
        :param state_secret: Secret used to encode the state JWT.
        :param redirect_url: Optional arbitrary redirect URL for the OAuth2 flow.
        If not given, the URL to the callback endpoint will be generated.
        """
        oauth_router = get_oauth_router(
            oauth_client,
            self.db,
            self._user_db_model,
            self.authenticator,
            state_secret,
            redirect_url,
        )

        for event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                oauth_router.add_event_handler(event_type, handler)

        self.oauth_routers.append(oauth_router)

        return oauth_router

    def _on_event(self, event_type: Event) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._event_handlers[event_type].append(func)
            self.router.add_event_handler(event_type, func)
            for oauth_router in self.oauth_routers:
                oauth_router.add_event_handler(event_type, func)
            return func

        return decorator
