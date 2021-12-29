import sys
from typing import Optional

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol  # pragma: no cover

from fastapi_users import models
from fastapi_users.manager import BaseUserManager


class Strategy(Protocol):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UC, models.UD]
    ) -> Optional[models.UD]:
        ...  # pragma: no cover

    async def write_token(self, user: models.UD) -> str:
        ...  # pragma: no cover
