import re
from inspect import Parameter, Signature
from typing import Sequence

from fastapi import Depends, HTTPException
from makefun import with_signature
from starlette import status

from fastapi_users.authentication.base import BaseAuthentication  # noqa: F401
from fastapi_users.authentication.cookie import CookieAuthentication  # noqa: F401
from fastapi_users.authentication.jwt import JWTAuthentication  # noqa: F401
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB

INVALID_CHARS_PATTERN = re.compile(r"[^0-9a-zA-Z_]")
INVALID_LEADING_CHARS_PATTERN = re.compile(r"^[^a-zA-Z_]+")


def name_to_variable_name(name: str) -> str:
    """Transform a backend name string into a string safe to use as variable name."""
    name = re.sub(INVALID_CHARS_PATTERN, "", name)
    name = re.sub(INVALID_LEADING_CHARS_PATTERN, "", name)
    return name


class DuplicateBackendNamesError(Exception):
    pass


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

        # Here comes some blood magic 🧙‍♂️
        # Thank to "makefun", we are able to generate callable
        # with a dynamic number of dependencies at runtime.
        # This way, each security schemes are detected by the OpenAPI generator.
        try:
            parameters = [
                Parameter(
                    name=name_to_variable_name(backend.name),
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(backend.scheme),  # type: ignore
                )
                for backend in self.backends
            ]
            signature = Signature(parameters)
        except ValueError:
            raise DuplicateBackendNamesError()

        @with_signature(signature, func_name="get_current_user")
        async def get_current_user(*args, **kwargs):
            return await self._authenticate(*args, **kwargs)

        @with_signature(signature, func_name="get_current_active_user")
        async def get_current_active_user(*args, **kwargs):
            user = await get_current_user(*args, **kwargs)
            if not user.is_active:
                raise self._get_credentials_exception()
            return user

        @with_signature(signature, func_name="get_current_superuser")
        async def get_current_superuser(*args, **kwargs):
            user = await get_current_active_user(*args, **kwargs)
            if not user.is_superuser:
                raise self._get_credentials_exception(status.HTTP_403_FORBIDDEN)
            return user

        self.get_current_user = get_current_user
        self.get_current_active_user = get_current_active_user
        self.get_current_superuser = get_current_superuser

    async def _authenticate(self, *args, **kwargs) -> BaseUserDB:
        for backend in self.backends:
            token: str = kwargs[name_to_variable_name(backend.name)]
            if token:
                user = await backend(token, self.user_db)
                if user is not None:
                    return user
        raise self._get_credentials_exception()

    def _get_credentials_exception(
        self, status_code: int = status.HTTP_401_UNAUTHORIZED
    ) -> HTTPException:
        return HTTPException(status_code=status_code)
