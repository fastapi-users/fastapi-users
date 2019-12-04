from typing import Sequence

from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from fastapi_users.authentication.base import BaseAuthentication  # noqa: F401
from fastapi_users.authentication.cookie import CookieAuthentication  # noqa: F401
from fastapi_users.authentication.jwt import JWTAuthentication  # noqa: F401
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class Authenticator:
    """
    Provides dependency callables to retrieve authenticated user.

    It performs the authentication against a list of backends
    defined by the end-developer. The first backend yielding a user wins.
    If no backend yields a user, an HTTPException is raised.

    :param backends: List of authentication backends.
    :param user_db: Database adapter instance.
    """

    backends: Sequence[BaseAuthentication]
    user_db: BaseUserDatabase

    def __init__(
        self, backends: Sequence[BaseAuthentication], user_db: BaseUserDatabase
    ):
        self.backends = backends
        self.user_db = user_db

    async def get_current_user(self, request: Request) -> BaseUserDB:
        return await self._authenticate(request)

    async def get_current_active_user(self, request: Request) -> BaseUserDB:
        user = await self.get_current_user(request)
        if not user.is_active:
            raise self._get_credentials_exception()
        return user

    async def get_current_superuser(self, request: Request) -> BaseUserDB:
        user = await self.get_current_active_user(request)
        if not user.is_superuser:
            raise self._get_credentials_exception(status.HTTP_403_FORBIDDEN)
        return user

    async def _authenticate(self, request: Request) -> BaseUserDB:
        for backend in self.backends:
            user = await backend(request, self.user_db)
            if user is not None:
                return user
        raise self._get_credentials_exception()

    def _get_credentials_exception(
        self, status_code: int = status.HTTP_401_UNAUTHORIZED
    ) -> HTTPException:
        return HTTPException(status_code=status_code)
