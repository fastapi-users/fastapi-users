from typing import Optional

from starlette.requests import Request

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class BaseAuthentication:
    """
    """

    async def __call__(
        self, request: Request, user_db: BaseUserDatabase
    ) -> Optional[BaseUserDB]:
        raise NotImplementedError()
