import sys
from typing import Any, Dict, Generic, Optional

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol  # pragma: no cover

from fastapi_users import models
from fastapi_users.authentication.token import UserTokenData
from fastapi_users.manager import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol):
    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[UserTokenData[models.UP, models.ID]]:
        ...  # pragma: no cover

    async def write_token(
        self,
        token_data: UserTokenData[models.UserProtocol[Any], Any],
    ) -> str:
        ...  # pragma: no cover

    async def destroy_token(
        self,
        token: str,
        user: models.UserProtocol[Any],
    ) -> None:
        ...  # pragma: no cover
