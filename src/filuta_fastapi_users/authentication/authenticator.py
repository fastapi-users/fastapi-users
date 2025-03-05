import re
from collections.abc import Callable, Sequence
from inspect import Parameter, Signature
from typing import Any, Generic, cast

from fastapi import Depends, HTTPException, status
from makefun import with_signature

from filuta_fastapi_users import models
from filuta_fastapi_users.authentication.backend import AuthenticationBackend
from filuta_fastapi_users.authentication.strategy.base import Strategy
from filuta_fastapi_users.manager import BaseUserManager, UserManagerDependency
from filuta_fastapi_users.types import DependencyCallable

INVALID_CHARS_PATTERN = re.compile(r"[^0-9a-zA-Z_]")
INVALID_LEADING_CHARS_PATTERN = re.compile(r"^[^a-zA-Z_]+")


def name_to_variable_name(name: str) -> str:
    """Transform a backend name string into a string safe to use as variable name."""
    name = re.sub(INVALID_CHARS_PATTERN, "", name)
    name = re.sub(INVALID_LEADING_CHARS_PATTERN, "", name)
    return name


def name_to_strategy_variable_name(name: str) -> str:
    """Transform a backend name string into a strategy variable name."""
    return f"strategy_{name_to_variable_name(name)}"


class DuplicateBackendNamesError(Exception):
    pass


EnabledBackendsDependency = DependencyCallable[Sequence[AuthenticationBackend[models.UP, models.ID, models.AP]]]


class Authenticator(Generic[models.UP, models.ID, models.AP]):
    """
    Provides dependency callables to retrieve authenticated user.

    It performs the authentication against a list of backends
    defined by the end-developer. The first backend yielding a user wins.
    If no backend yields a user, an HTTPException is raised.

    :param backends: List of authentication backends.
    :param get_user_manager: User manager dependency callable.
    """

    backends: Sequence[AuthenticationBackend[models.UP, models.ID, models.AP]]

    def __init__(
        self,
        backends: Sequence[AuthenticationBackend[models.UP, models.ID, models.AP]],
        get_user_manager: UserManagerDependency[models.UP, models.ID],
    ):
        self.backends = backends
        self.get_user_manager = get_user_manager

    def current_user_token(  # noqa: PLR0913
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        poweruser: bool = False,
        authorized: bool = True,
        ignore_expired: bool = False,
        get_enabled_backends: EnabledBackendsDependency[models.UP, models.ID, models.AP] | None = None,
    ) -> Callable[[Any], tuple[models.UP | None, str | None]]:
        """
        Return a dependency callable to retrieve currently authenticated user and token.

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
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_token_dependency(*args, **kwargs) -> tuple[models.UP | None, str | None]:  # type: ignore
            return await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                poweruser=poweruser,
                authorized=authorized,
                ignore_expired=ignore_expired,
                **kwargs,
            )

        return current_user_token_dependency

    def current_user(  # type: ignore  # noqa: PLR0913
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        poweruser: bool = False,
        authorized: bool = True,
        ignore_expired: bool = False,
        get_enabled_backends: EnabledBackendsDependency[models.UP, models.ID, models.AP] | None = None,
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
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):  # type: ignore
            user, _ = await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                poweruser=poweruser,
                authorized=authorized,
                ignore_expired=ignore_expired,
                **kwargs,
            )
            return user

        return current_user_dependency

    async def _authenticate(  # noqa: PLR0913, C901
        self,
        *args: Any,
        user_manager: BaseUserManager[models.UP, models.ID],
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        poweruser: bool = False,
        authorized: bool = False,
        ignore_expired: bool = False,
        **kwargs: Any,
    ) -> tuple[models.UP | None, str | None]:
        user: models.UP | None = None
        token: str | None = None
        enabled_backends: Sequence[AuthenticationBackend[models.UP, models.ID, models.AP]] = kwargs.get(
            "enabled_backends", self.backends
        )

        detail = "no-user"

        for backend in self.backends:
            if backend in enabled_backends:
                token = kwargs[name_to_variable_name(backend.name)]
                strategy: Strategy[models.UP, models.ID, models.AP] = kwargs[
                    name_to_strategy_variable_name(backend.name)
                ]
                if token is not None:
                    user = await strategy.read_token(token, user_manager, authorized, ignore_expired)
                    if user is not None:
                        break

        status_code = status.HTTP_401_UNAUTHORIZED
        if user is not None:
            status_code = status.HTTP_403_FORBIDDEN
            detail = "no-reason"
            if active and not user.is_active:
                status_code = status.HTTP_401_UNAUTHORIZED
                user = None
                detail = "no-active"
            elif verified and not user.is_verified:
                user = None
                detail = "no-verified"
            elif superuser and not user.is_superuser:
                user = None
                detail = "no-permissions"
            elif poweruser and not user.is_poweruser:
                user = None
                detail = "no-permissions"
        if user is None and not optional:
            raise HTTPException(status_code=status_code, detail=detail)
        return user, token

    def _get_dependency_signature(
        self, get_enabled_backends: EnabledBackendsDependency[models.UP, models.ID, models.AP] | None = None
    ) -> Signature:
        """
        Generate a dynamic signature for the current_user dependency.

        Here comes some blood magic 🧙‍♂️
        Thank to "makefun", we are able to generate callable
        with a dynamic number of dependencies at runtime.
        This way, each security schemes are detected by the OpenAPI generator.
        """
        try:
            parameters: list[Parameter] = [
                Parameter(
                    name="user_manager",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(self.get_user_manager),
                )
            ]

            for backend in self.backends:
                parameters += [
                    Parameter(
                        name=name_to_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(cast(Callable, backend.transport.scheme)),  # type: ignore
                    ),
                    Parameter(
                        name=name_to_strategy_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(backend.get_strategy),
                    ),
                ]

            if get_enabled_backends is not None:
                parameters += [
                    Parameter(
                        name="enabled_backends",
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(get_enabled_backends),
                    )
                ]
            return Signature(parameters)
        except ValueError:
            raise DuplicateBackendNamesError()
