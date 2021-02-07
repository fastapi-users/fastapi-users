import re
from inspect import Parameter, Signature, signature
from typing import Optional, Sequence

from deprecated import deprecated
from fastapi import Depends, HTTPException, status
from makefun import with_signature

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

        self.get_current_user = self._deprecated_current_user("get_current_user")
        self.get_current_active_user = self._deprecated_current_user(
            "get_current_active_user", active=True
        )
        self.get_current_verified_user = self._deprecated_current_user(
            "get_current_verified_user", active=True, verified=True
        )
        self.get_current_superuser = self._deprecated_current_user(
            "get_current_superuser", active=True, superuser=True
        )
        self.get_current_verified_superuser = self._deprecated_current_user(
            "get_current_verified_superuser",
            active=True,
            verified=True,
            superuser=True,
        )
        self.get_optional_current_user = self._deprecated_current_user(
            "get_optional_current_user", optional=True
        )
        self.get_optional_current_active_user = self._deprecated_current_user(
            "get_optional_current_active_user", optional=True, active=True
        )
        self.get_optional_current_verified_user = self._deprecated_current_user(
            "get_optional_current_verified_user",
            optional=True,
            active=True,
            verified=True,
        )
        self.get_optional_current_superuser = self._deprecated_current_user(
            "get_optional_current_superuser", optional=True, active=True, superuser=True
        )
        self.get_optional_current_verified_superuser = self._deprecated_current_user(
            "get_optional_current_verified_superuser",
            optional=True,
            active=True,
            verified=True,
            superuser=True,
        )

    def current_user(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
    ):
        """
        Return a dependency callable to retrieve currently authenticated user.

        :param optional: If `True`, `None` is returned if there is no authenticated user
        or if it doesn't pass the other requirements.
        Otherwise, throw `401 Unauthorized`. Defaults to `False`.
        Otherwise, an exception is raised. Defaults to `False`.
        :param active: If `True`, throw `401 Unauthorized` if
        the authenticated user is inactive. Defaults to `False`.
        :param verified: If `True`, throw `401 Unauthorized` if
        the authenticated user is not verified. Defaults to `False`.
        :param superuser: If `True`, throw `403 Forbidden` if
        the authenticated user is not a superuser. Defaults to `False`.
        """
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

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):
            return await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                **kwargs
            )

        return current_user_dependency

    def _deprecated_current_user(
        self,
        func_name: str,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
    ):
        current_user_dependency = self.current_user(
            optional, active, verified, superuser
        )

        @deprecated(
            version="5.1.0",
            reason=(
                "You should call `current_user` with your own set of parameters. "
                "See: "
                "https://frankie567.github.io/fastapi-users/usage/dependency-callables/"
            ),
        )
        @with_signature(signature(current_user_dependency), func_name=func_name)
        async def deprecated_current_user_dependency(*args, **kwargs):
            return await current_user_dependency(*args, **kwargs)

        return deprecated_current_user_dependency

    async def _authenticate(
        self,
        *args,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        **kwargs
    ) -> Optional[BaseUserDB]:
        user: Optional[BaseUserDB] = None
        for backend in self.backends:
            token: str = kwargs[name_to_variable_name(backend.name)]
            if token:
                user = await backend(token, self.user_db)
                if user:
                    break

        status_code = status.HTTP_401_UNAUTHORIZED
        if user:
            if active and not user.is_active:
                user = None
            elif verified and not user.is_verified:
                user = None
            elif superuser and not user.is_superuser:
                status_code = status.HTTP_403_FORBIDDEN
                user = None

        if not user and not optional:
            raise HTTPException(status_code=status_code)
        return user
