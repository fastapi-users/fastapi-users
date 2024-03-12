from typing import Generic, Optional, Protocol

from fastapi_users import models
from fastapi_users.authentication.models import (
    AccessRefreshToken,
    TokenIdentityType,
    TokenType,
)
from fastapi_users.manager import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class BaseStrategy(
    Protocol,
    Generic[
        models.UP,
        models.ID,
        TokenIdentityType,
        TokenType,
    ],
):  # type: ignore
    async def read_token(
        self,
        token: Optional[TokenIdentityType],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[models.UP]: ...  # pragma: no cover
    async def write_token(self, user: models.UP) -> TokenType: ...  # pragma: no cover
    async def destroy_token(
        self, token: TokenIdentityType, user: models.UP
    ) -> None: ...  # pragma: no cover


class Strategy(
    BaseStrategy[models.UP, models.ID, str, str], Generic[models.UP, models.ID]
):
    pass


class StrategyRefresh(
    BaseStrategy[models.UP, models.ID, str, AccessRefreshToken],
    Generic[models.UP, models.ID],
):
    async def read_token_by_refresh(
        self,
        refresh_token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[models.UP]: ...  # pragma: no cover

    async def destroy_token_by_refresh(
        self,
        refresh_token: Optional[str],
        user: models.UP,
    ) -> None: ...  # pragma: no cover
