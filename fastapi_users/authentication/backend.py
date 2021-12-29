from typing import Any, Generic

from fastapi import Response

from fastapi_users import models
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.authentication.transport import Transport


class BackendWithoutLogoutError(RuntimeError):
    pass


class AuthenticationBackend(Generic[models.UC, models.UD]):
    """
    Base authentication backend.

    Every backend should derive from this class.

    :param name: Name of the backend.
    :param transport: TODO
    :param strategy: TODO
    """

    name: str
    transport: Transport
    strategy: Strategy[models.UC, models.UD]

    def __init__(
        self, name: str, transport: Transport, strategy: Strategy[models.UC, models.UD]
    ):
        self.name = name
        self.transport = transport
        self.strategy = strategy

    def has_logout(self) -> bool:
        return self.transport.has_logout

    async def get_login_response(self, user: models.UD, response: Response) -> Any:
        token = await self.strategy.write_token(user)
        return await self.transport.get_login_response(token, response)

    async def get_logout_response(self, response: Response) -> Any:
        if not self.has_logout():
            raise BackendWithoutLogoutError()

        return await self.transport.get_logout_response(response)
