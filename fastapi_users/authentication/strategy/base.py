from typing import Generic, Optional, Protocol

from fastapi_users import models
from fastapi_users.authentication.models import AccessRefreshToken
from fastapi_users.manager import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol, Generic[models.UP, models.ID]):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]: ...  # pragma: no cover

    async def write_token(self, user: models.UP) -> str: ...  # pragma: no cover

    async def destroy_token(
        self, token: str, user: models.UP
    ) -> None: ...  # pragma: no cover


class StrategyRefresh(Strategy[models.UP, models.ID], Generic[models.UP, models.ID]):
    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
        refresh_token: Optional[str] = None,
    ) -> Optional[models.UP]: ...  # pragma: no cover

    async def write_token(
        self, user: models.UP
    ) -> AccessRefreshToken: ...  # pragma: no cover  # noqa: F821

    async def destroy_token(
        self,
        token: Optional[str],
        user: models.UP,
        refresh_token: Optional[str] = None,
    ) -> None: ...  # pragma: no cover
