from typing import Callable

from starlette.responses import Response

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import UserDB


class BaseAuthentication:

    user_db: BaseUserDatabase

    def __init__(self, user_db: BaseUserDatabase):
        self.user_db = user_db

    async def get_login_response(self, user: UserDB, response: Response):
        raise NotImplementedError()

    def get_authentication_method(self) -> Callable[..., UserDB]:
        raise NotImplementedError()
