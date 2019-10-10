from typing import Callable, Type

from fastapi import APIRouter

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUser, BaseUserDB
from fastapi_users.router import get_user_router


class FastAPIUsers:
    """
    Main object that ties together the component for users authentication.

    :param db: Database adapter instance.
    :param auth: Authentication logic instance.
    :param user_model: Pydantic model of a user.

    :attribute router: FastAPI router exposing authentication routes.
    :attribute get_current_user: Dependency callable to inject authenticated user.
    """

    db: BaseUserDatabase
    auth: BaseAuthentication
    router: APIRouter
    get_current_user: Callable[..., BaseUserDB]

    def __init__(
        self, db: BaseUserDatabase, auth: BaseAuthentication, user_model: Type[BaseUser]
    ):
        self.db = db
        self.auth = auth
        self.router = get_user_router(self.db, user_model, self.auth)

        get_current_user = self.auth.get_authentication_method(self.db)
        self.get_current_user = get_current_user  # type: ignore
