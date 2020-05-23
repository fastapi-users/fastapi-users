from typing import Any, Optional

import jwt
from fastapi import Response
from fastapi.security import APIKeyCookie
from pydantic import UUID4

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt


class CookieAuthentication(BaseAuthentication[str]):
    """
    Authentication backend using a cookie.

    Internally, uses a JWT token to store the data.

    :param secret: Secret used to encode the cookie.
    :param lifetime_seconds: Lifetime duration of the cookie in seconds.
    :param cookie_name: Name of the cookie.
    :param cookie_path: Cookie path.
    :param cookie_domain: Cookie domain.
    :param cookie_secure: Whether to only send the cookie to the server via SSL request.
    :param cookie_httponly: Whether to prevent access to the cookie via JavaScript.
    :param name: Name of the backend. It will be used to name the login route.
    """

    scheme: APIKeyCookie
    token_audience: str = "fastapi-users:auth"
    secret: str
    lifetime_seconds: int
    cookie_name: str
    cookie_path: str
    cookie_domain: Optional[str]
    cookie_secure: bool
    cookie_httponly: bool

    def __init__(
        self,
        secret: str,
        lifetime_seconds: int,
        cookie_name: str = "fastapiusersauth",
        cookie_path: str = "/",
        cookie_domain: str = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        name: str = "cookie",
    ):
        super().__init__(name, logout=True)
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.cookie_name = cookie_name
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)

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
        response.set_cookie(
            self.cookie_name,
            token,
            max_age=self.lifetime_seconds,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
        )

        # We shouldn't return directly the response
        # so that FastAPI can terminate it properly
        return None

    async def get_logout_response(self, user: BaseUserDB, response: Response) -> Any:
        response.delete_cookie(
            self.cookie_name, path=self.cookie_path, domain=self.cookie_domain
        )

    async def _generate_token(self, user: BaseUserDB) -> str:
        data = {"user_id": str(user.id), "aud": self.token_audience}
        return generate_jwt(data, self.lifetime_seconds, self.secret, JWT_ALGORITHM)
