import enum
import re
from inspect import Parameter, Signature
from typing import Callable, Optional, Sequence

from fastapi import Depends, HTTPException, status
from makefun import with_signature

from fastapi_users import models
from fastapi_users.authentication.base import BaseAuthentication  # noqa: F401
from fastapi_users.authentication.cookie import CookieAuthentication  # noqa: F401
from fastapi_users.authentication.jwt import JWTAuthentication  # noqa: F401
from fastapi_users.manager import BaseUserManager, UserManagerDependency

INVALID_CHARS_PATTERN = re.compile(r"[^0-9a-zA-Z_]")
INVALID_LEADING_CHARS_PATTERN = re.compile(r"^[^a-zA-Z_]+")


def name_to_variable_name(name: str) -> str:
    """Transform a backend name string into a string safe to use as variable name."""
    name = re.sub(INVALID_CHARS_PATTERN, "", name)
    name = re.sub(INVALID_LEADING_CHARS_PATTERN, "", name)
    return name


class DuplicateBackendNamesError(Exception):
    pass


EnabledBackendsDependency = Callable[..., Sequence[BaseAuthentication]]


class Authenticator:
    """
    Provides dependency callables to retrieve authenticated user.

    It performs the authentication against a list of backends
    defined by the end-developer. The first backend yielding a user wins.
    If no backend yields a user, an HTTPException is raised.

    :param backends: List of authentication backends.
    :param get_user_manager: User manager dependency callable.
    """

    backends: Sequence[BaseAuthentication]
    backends_enum: enum.Enum

    def __init__(
        self,
        backends: Sequence[BaseAuthentication],
        get_user_manager: UserManagerDependency[models.UC, models.UD],
    ):
        self.backends = backends
        self.backends_enum = enum.Enum(  # type: ignore
            "AuthenticationBackendName",
            {backend.name: backend.name for backend in backends},  # type: ignore
        )
        self.get_user_manager = get_user_manager

    def current_user(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        get_enabled_backends: Optional[EnabledBackendsDependency] = None,
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
        :param get_enabled_backends: Optional dependency callable returning
        a list of enabled authentication backends.
        Useful if you want to dynamically enable some authentication backends
        based on external logic, like a configuration in database.
        By default, all specified authentication backends are enabled.
        Please not however that every backends will appear in the OpenAPI documentation,
        as FastAPI resolves it statically.
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
            ] + [
                Parameter(
                    name="user_manager",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(self.get_user_manager),
                )
            ]
            if get_enabled_backends is not None:
                parameters += [
                    Parameter(
                        name="enabled_backends",
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(get_enabled_backends),
                    )
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

    async def _authenticate(
        self,
        *args,
        user_manager: BaseUserManager[models.UC, models.UD],
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        **kwargs
    ) -> Optional[models.UD]:
        user: Optional[models.UD] = None
        enabled_backends: Sequence[BaseAuthentication] = kwargs.get(
            "enabled_backends", self.backends
        )
        for backend in self.backends:
            if backend in enabled_backends:
                token: str = kwargs[name_to_variable_name(backend.name)]
                if token:
                    user = await backend(token, user_manager)
                    if user:
                        break

        status_code = status.HTTP_401_UNAUTHORIZED
        if user:
            status_code = status.HTTP_403_FORBIDDEN
            if active and not user.is_active:
                status_code = status.HTTP_401_UNAUTHORIZED
                user = None
            elif (
                verified and not user.is_verified or superuser and not user.is_superuser
            ):
                user = None
        if not user and not optional:
            raise HTTPException(status_code=status_code)
        return user
