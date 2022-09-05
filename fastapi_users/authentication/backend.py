from datetime import datetime
from typing import Any, Generic, Optional, Set

from fastapi import Response

from fastapi_users import models
from fastapi_users.authentication.strategy import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.authentication.token import UserTokenData
from fastapi_users.authentication.transport import (
    LoginT,
    LogoutT,
    Transport,
    TransportLogoutNotSupportedError,
    TransportTokenResponse,
)
from fastapi_users.scopes import SystemScope
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
        get_strategy: DependencyCallable[Strategy],
        access_token_lifetime_seconds: Optional[int] = 3600,
        refresh_token_enabled: bool = False,
        refresh_token_lifetime_seconds: Optional[int] = 86400,
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy
        self.access_token_lifetime_seconds = access_token_lifetime_seconds
        self.refresh_token_enabled = refresh_token_enabled
        self.refresh_token_lifetime_seconds = refresh_token_lifetime_seconds

    async def login(
        self,
        strategy: Strategy,
        user: models.UserProtocol[Any],
        response: Response,
        last_authenticated: Optional[datetime] = None,
    ) -> Optional[LoginT]:
        scopes: Set[str] = set()
        if user.is_active:
            scopes.add(SystemScope.USER)
        if user.is_verified:
            scopes.add(SystemScope.VERIFIED)
        if user.is_superuser:
            scopes.add(SystemScope.SUPERUSER)

        access_token_data = UserTokenData.issue_now(
            user,
            self.access_token_lifetime_seconds,
            last_authenticated,
            scopes=scopes,
        )
        token_response = TransportTokenResponse(
            access_token=await strategy.write_token(access_token_data)
        )
        if self.refresh_token_enabled:
            refresh_token_data = UserTokenData.issue_now(
                user,
                self.refresh_token_lifetime_seconds,
                last_authenticated,
                scopes={SystemScope.REFRESH},
            )
            token_response.refresh_token = await strategy.write_token(
                refresh_token_data
            )
        return await self.transport.get_login_response(token_response, response)

    async def logout(
        self,
        strategy: Strategy,
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
