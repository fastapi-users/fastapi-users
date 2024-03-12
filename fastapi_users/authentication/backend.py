from typing import Generic, Optional, TypeVar

from fastapi import Response, status

from fastapi_users import models
from fastapi_users.authentication.models import AccessRefreshToken
from fastapi_users.authentication.strategy import (
    BaseStrategy,
    StrategyDestroyNotSupportedError,
    StrategyRefresh,
)
from fastapi_users.authentication.transport import (
    BaseTransport,
    TransportLogoutNotSupportedError,
    TransportRefresh,
)
from fastapi_users.manager import BaseUserManager
from fastapi_users.types import DependencyCallable

TokenType = TypeVar("TokenType")


class BaseAuthenticationBackend(Generic[models.UP, models.ID, TokenType]):
    """
    Combination of an authentication transport and strategy.

    Together, they provide a full authentication method logic.

    :param name: Name of the backend.
    :param transport: Authentication transport instance.
    :param get_strategy: Dependency callable returning
    an authentication strategy instance.
    """

    name: str
    transport: BaseTransport[TokenType]

    def __init__(
        self,
        name: str,
        transport: BaseTransport[TokenType],
        get_strategy: DependencyCallable[
            BaseStrategy[models.UP, models.ID, str, TokenType]
        ],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def login(
        self,
        strategy: BaseStrategy[models.UP, models.ID, str, TokenType],
        user: models.UP,
    ) -> Response:
        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token)

    async def logout(
        self,
        strategy: BaseStrategy[models.UP, models.ID, str, TokenType],
        user: models.UP,
        token: str,
    ) -> Response:
        try:
            await strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response


class AuthenticationBackend(
    BaseAuthenticationBackend[models.UP, models.ID, str], Generic[models.UP, models.ID]
):
    pass


class AuthenticationBackendRefresh(
    BaseAuthenticationBackend[models.UP, models.ID, AccessRefreshToken],
    Generic[models.UP, models.ID],
):
    transport: TransportRefresh

    def __init__(
        self,
        name: str,
        transport: TransportRefresh,
        get_strategy: DependencyCallable[StrategyRefresh[models.UP, models.ID]],
    ):
        super().__init__(name, transport, get_strategy)

    async def refresh(
        self,
        strategy: StrategyRefresh[models.UP, models.ID],
        user_manager: BaseUserManager[models.UP, models.ID],
        refresh_token: str,
    ) -> Optional[Response]:
        user = await strategy.read_token_by_refresh(
            refresh_token=refresh_token, user_manager=user_manager
        )
        if user is not None:
            await strategy.destroy_token_by_refresh(
                user=user, refresh_token=refresh_token
            )
            token = await strategy.write_token(user)
            return await self.transport.get_login_response(token)
        return None
