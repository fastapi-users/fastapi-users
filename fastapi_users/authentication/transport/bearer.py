from typing import Any, Dict, Optional

from fastapi import Response, status
from fastapi.security import OAuth2, OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from pydantic import BaseModel

from fastapi_users.authentication.transport.base import (
    Transport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.openapi import OpenAPIResponseType


class BearerResponse(BaseModel):
    access_token: str
    token_type: str


class BearerTransport(Transport):
    scheme: OAuth2

    def __init__(
        self,
        tokenUrl: str,
        authorizationUrl: Optional[str] = None,
        refreshUrl: Optional[str] = None,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = False,
        grant_type: str = "password",
    ):
        if grant_type == "password":
            self.scheme = OAuth2PasswordBearer(
                tokenUrl,
                scheme_name,
                scopes,
                description,
                auto_error,
            )
        elif grant_type == "authorization_code":
            assert authorizationUrl
            self.scheme = OAuth2AuthorizationCodeBearer(
                authorizationUrl,
                tokenUrl,
                refreshUrl,
                scheme_name,
                scopes,
                description,
                auto_error,
            )
        else:
            raise ValueError(f"Unsupported grant type: {grant_type}")

    async def get_login_response(self, token: str, response: Response) -> Any:
        return BearerResponse(access_token=token, token_type="bearer")

    async def get_logout_response(self, response: Response) -> Any:
        raise TransportLogoutNotSupportedError()

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
                            "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
                            "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
                            "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
                            "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}
