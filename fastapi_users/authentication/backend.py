from typing import Any, Generic

from fastapi import Response

from fastapi_users import models
from fastapi_users.authentication.strategy import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.authentication.transport import (
    LoginT,
    LogoutT,
    Transport,
    TransportLogoutNotSupportedError,
    TransportTokenResponse,
)
from fastapi_users.types import DependencyCallable


class AuthenticationBackend(Generic[LoginT, LogoutT]):
    """
    Combination of an authentication transport and strategy.

    Together, they provide a full authentication method logic.

    :param name: Name of the backend.
    :param transport: Authentication transport instance.
    :param get_strategy: Dependency callable returning
    an authentication strategy instance.
    """

    name: str
    transport: Transport[LoginT, LogoutT]

    def __init__(
        self,
        name: str,
        transport: Transport[LoginT, LogoutT],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def login(
        self,
        strategy: Strategy[models.UP, models.ID],
        user: models.UserProtocol[Any],
        response: Response,
    ) -> Optional[LoginT]:
        token_response = TransportTokenResponse(
            access_token=await strategy.write_token(user)
        )
        return await self.transport.get_login_response(token_response, response)

    async def logout(
        self,
        strategy: Strategy[models.UP, models.ID],
        user: models.UserProtocol[Any],
        token: str,
        response: Response,
    ) -> Optional[LogoutT]:
        try:
            await strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            await self.transport.get_logout_response(response)
        except TransportLogoutNotSupportedError:
            return None
