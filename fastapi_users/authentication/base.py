from typing import Callable

from starlette.responses import Response

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class BaseAuthentication:
    """Base adapter for generating and decoding authentication tokens."""

    async def get_login_response(self, user: BaseUserDB, response: Response):
        raise NotImplementedError()

    def get_authentication_method(
        self, user_db: BaseUserDatabase
    ) -> Callable[..., BaseUserDB]:
        raise NotImplementedError()
