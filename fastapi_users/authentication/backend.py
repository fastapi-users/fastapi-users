from typing import Any, Callable, Generic

from fastapi import Response

from fastapi_users import models
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.authentication.transport import Transport


class AuthenticationBackend(Generic[models.UC, models.UD]):
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
        get_strategy: Callable[..., Strategy[models.UC, models.UD]],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    def has_logout(self) -> bool:
        return self.transport.has_logout

    async def get_login_response(
        self,
        strategy: Strategy[models.UC, models.UD],
        user: models.UD,
        response: Response,
    ) -> Any:
        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token, response)

    async def get_logout_response(
        self, strategy: Strategy[models.UC, models.UD], response: Response
    ) -> Any:
        return await self.transport.get_logout_response(response)
