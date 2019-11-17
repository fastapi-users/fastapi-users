from typing import Any, Optional

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import Response

from fastapi_users.authentication.base import BaseAuthentication
from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt


class JWTAuthentication(BaseAuthentication):
    """
    Authentication using a JWT.

    :param secret: Secret used to encode the JWT.
    :param lifetime_seconds: Lifetime duration of the JWT in seconds.
    """

    token_audience: str = "fastapi-users:auth"
    secret: str
    lifetime_seconds: int

    def __init__(
        self,
        secret: str,
        lifetime_seconds: int,
        tokenUrl: str = "/users/login",
        name: str = "jwt",
    ):
        super().__init__(name)
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.scheme = OAuth2PasswordBearer(tokenUrl, auto_error=False)

    async def __call__(
        self, request: Request, user_db: BaseUserDatabase,
    ) -> Optional[BaseUserDB]:
        token = await self.scheme.__call__(request)
        if token is None:
            return None

        try:
            data = jwt.decode(
                token,
                self.secret,
                audience=self.token_audience,
                algorithms=[JWT_ALGORITHM],
            )
            user_id = data.get("user_id")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None
        return await user_db.get(user_id)

    async def get_login_response(self, user: BaseUserDB, response: Response) -> Any:
        data = {"user_id": user.id, "aud": self.token_audience}
        token = generate_jwt(data, self.lifetime_seconds, self.secret, JWT_ALGORITHM)

        return {"token": token}
