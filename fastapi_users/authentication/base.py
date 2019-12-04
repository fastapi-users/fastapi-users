from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import Response

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class BaseAuthentication:
    """
    Base authentication backend.

    Every backend should derive from this class.

    :param name: Name of the backend. It will be used to name the login route.
    """

    name: str

    def __init__(self, name: str = "base"):
        self.name = name

    async def __call__(
        self, request: Request, user_db: BaseUserDatabase
    ) -> Optional[BaseUserDB]:
        raise NotImplementedError()

    async def get_login_response(self, user: BaseUserDB, response: Response) -> Any:
        raise NotImplementedError()
