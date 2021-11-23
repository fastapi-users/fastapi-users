from typing import Any, Dict, Generic, List, Optional

import jwt
from fastapi import Response, status
from fastapi.security import APIKeyCookie
from pydantic import UUID4

from fastapi_users import models
from fastapi_users.authentication import BaseAuthentication
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager, UserNotExists


class CookieAuthentication(
    Generic[models.UC, models.UD], BaseAuthentication[str, models.UC, models.UD]
):
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
    :param cookie_samesite: Set the SameSite policy of the cookie.
    :param name: Name of the backend. It will be used to name the login route.
    :param token_audience: List of valid audiences for the JWT.
    """

    scheme: APIKeyCookie
    token_audience: List[str]
    secret: SecretType
    lifetime_seconds: Optional[int]
    cookie_name: str
    cookie_path: str
    cookie_domain: Optional[str]
    cookie_secure: bool
    cookie_httponly: bool
    cookie_samesite: str

    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: Optional[int] = None,
        cookie_name: str = "fastapiusersauth",
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: str = "lax",
        name: str = "cookie",
        token_audience: List[str] = ["fastapi-users:auth"],
    ):
        super().__init__(name, logout=True)
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.cookie_name = cookie_name
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.token_audience = token_audience
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)

    async def __call__(
        self,
        credentials: Optional[str],
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Optional[models.UD]:
        if credentials is None:
            return None

        try:
            data = decode_jwt(credentials, self.secret, self.token_audience)
            user_id = data.get("user_id")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            user_uiid = UUID4(user_id)
            return await user_manager.get(user_uiid)
        except ValueError:
            return None
        except UserNotExists:
            return None

    async def get_login_response(
        self,
        user: models.UD,
        response: Response,
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Any:
        token = await self._generate_token(user)
        response.set_cookie(
            self.cookie_name,
            token,
            max_age=self.lifetime_seconds,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

        # We shouldn't return directly the response
        # so that FastAPI can terminate it properly
        return None

    def get_openapi_login_responses_success(self) -> Dict[str, Any]:
        return {status.HTTP_200_OK: {"model": None}}

    async def get_logout_response(
        self,
        user: models.UD,
        response: Response,
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Any:
        response.delete_cookie(
            self.cookie_name, path=self.cookie_path, domain=self.cookie_domain
        )

    def get_openapi_logout_responses_success(self) -> Dict[str, Any]:
        return {status.HTTP_200_OK: {"model": None}}

    async def _generate_token(self, user: models.UD) -> str:
        data = {"user_id": str(user.id), "aud": self.token_audience}
        return generate_jwt(data, self.secret, self.lifetime_seconds)
