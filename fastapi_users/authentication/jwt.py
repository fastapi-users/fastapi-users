from typing import Any, Optional

import jwt
from fastapi import Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4

from fastapi_users.authentication.base import BaseAuthentication
from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt


class JWTAuthentication(BaseAuthentication[str]):
    """
    Authentication backend using a JWT in a Bearer header.

    :param secret: Secret used to encode the JWT.
    :param lifetime_seconds: Lifetime duration of the JWT in seconds.
    :param tokenUrl: Path where to get a token.
    :param name: Name of the backend. It will be used to name the login route.
    """

    scheme: OAuth2PasswordBearer
    token_audience: str = "fastapi-users:auth"
    secret: str
    lifetime_seconds: int

    def __init__(
        self,
        secret: str,
        lifetime_seconds: int,
        tokenUrl: str = "/login",
        name: str = "jwt",
    ):
        super().__init__(name, logout=False)
        self.scheme = OAuth2PasswordBearer(tokenUrl, auto_error=False)
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds

    async def __call__(
        self, credentials: Optional[str], user_db: BaseUserDatabase,
    ) -> Optional[BaseUserDB]:
        if credentials is None:
            return None

        try:
            data = jwt.decode(
                credentials,
                self.secret,
                audience=self.token_audience,
                algorithms=[JWT_ALGORITHM],
            )
            user_id = data.get("user_id")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            user_uiid = UUID4(user_id)
            return await user_db.get(user_uiid)
        except ValueError:
            return None

    async def get_login_response(self, user: BaseUserDB, response: Response) -> Any:
        token = await self._generate_token(user)
        return {"access_token": token, "token_type": "bearer"}

    async def _generate_token(self, user: BaseUserDB) -> str:
        data = {"user_id": str(user.id), "aud": self.token_audience}
        return generate_jwt(data, self.lifetime_seconds, self.secret, JWT_ALGORITHM)
