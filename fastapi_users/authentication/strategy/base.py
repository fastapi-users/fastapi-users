import sys
from typing import Generic, Optional

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol  # pragma: no cover

from fastapi_users import models
from fastapi_users.manager import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol, Generic[models.UC, models.UD]):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UC, models.UD]
    ) -> Optional[models.UD]:
        ...  # pragma: no cover

    async def write_token(self, user: models.UD) -> str:
        ...  # pragma: no cover

    async def destroy_token(self, token: str, user: models.UD) -> None:
        ...  # pragma: no cover
