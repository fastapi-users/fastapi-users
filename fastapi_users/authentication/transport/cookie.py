from typing import Literal, Optional

from fastapi import Response, status
from fastapi.security import APIKeyCookie

from fastapi_users.authentication.transport.base import Transport
from fastapi_users.openapi import OpenAPIResponseType


class CookieTransport(Transport):
    scheme: APIKeyCookie

    def __init__(
        self,
        cookie_name: str = "fastapiusersauth",
        cookie_max_age: Optional[int] = None,
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
        on_login_redirect_url: Optional[str] = None,
    ):
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)
        self.on_login_redirect_url = on_login_redirect_url


    async def get_login_response(self, token: str) -> Response:
        if self.on_login_redirect_url:
            response = RedirectResponse(url=self.on_login_redirect_url, status_code=status.HTTP_302_FOUND)
        else:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self._set_login_cookie(response, token)

    async def get_logout_response(self) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self._set_logout_cookie(response)

    def _set_login_cookie(self, response: Response, token: str) -> Response:
        response.set_cookie(
            self.cookie_name,
            token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response

    def _set_logout_cookie(self, response: Response) -> Response:
        response.set_cookie(
            self.cookie_name,
            "",
            max_age=0,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {status.HTTP_204_NO_CONTENT: {"model": None}}

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {status.HTTP_204_NO_CONTENT: {"model": None}}
