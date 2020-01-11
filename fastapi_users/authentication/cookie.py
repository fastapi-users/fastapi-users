from typing import Any, Optional

from fastapi.security import APIKeyCookie
from starlette.requests import Request
from starlette.responses import Response

from fastapi_users.authentication.jwt import JWTAuthentication
from fastapi_users.models import BaseUserDB


class CookieAuthentication(JWTAuthentication):
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
        super().__init__(secret, lifetime_seconds, name=name)
        self.lifetime_seconds = lifetime_seconds
        self.cookie_name = cookie_name
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.api_key_cookie = APIKeyCookie(name=self.cookie_name, auto_error=False)

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

    async def _retrieve_token(self, request: Request) -> Optional[str]:
        return await self.api_key_cookie.__call__(request)
