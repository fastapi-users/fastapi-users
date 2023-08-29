from typing import Generic

from fastapi import Response, status

from filuta_fastapi_users import models
from filuta_fastapi_users.authentication.strategy.base import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from filuta_fastapi_users.authentication.transport.base import (
    Transport,
    TransportLogoutNotSupportedError,
)
from filuta_fastapi_users.types import DependencyCallable


class AuthenticationBackend(Generic[models.UP, models.ID, models.AP]):
    """
    Combination of an authentication transport and strategy.

    Together, they provide a full authentication method logic.

    :param name: Name of the backend.
    :param transport: Authentication transport instance.
    :param get_strategy: Dependency callable returning
    an authentication strategy instance.
    """

    name: str
    transport: Transport

    def __init__(
        self,
        name: str,
        transport: Transport,
        get_strategy: DependencyCallable[Strategy[models.UP, models.ID, models.AP]],
    ) -> None:
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def abd(self) -> None:
        pass

    async def login(
        self, strategy: Strategy[models.UP, models.ID, models.AP], user: models.UP, refresh_token: str
    ) -> Response:
        record = await strategy.write_token(user)
        return await self.transport.get_login_response(record, refresh_token)

    async def logout(self, strategy: Strategy[models.UP, models.ID, models.AP], token: str) -> Response:
        try:
            await strategy.destroy_token(token)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response
