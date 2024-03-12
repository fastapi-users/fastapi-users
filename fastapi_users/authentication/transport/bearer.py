from abc import abstractmethod
from typing import Generic, TypeVar

from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from fastapi_users.authentication.models import AccessRefreshToken
from fastapi_users.authentication.transport.base import (
    BaseTransport,
    Transport,
    TransportLogoutNotSupportedError,
    TransportRefresh,
)
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.schemas import model_dump

TokenType = TypeVar("TokenType")


class BearerResponse(BaseModel):
    access_token: str
    token_type: str


class BaseBearerTransport(BaseTransport[TokenType], Generic[TokenType]):
    scheme: OAuth2PasswordBearer

    def __init__(self, tokenUrl: str):
        self.scheme = OAuth2PasswordBearer(tokenUrl, auto_error=False)

    @abstractmethod
    async def get_login_response(
        self, token: TokenType
    ) -> Response: ...  # pragma: no cover

    async def get_logout_response(self) -> Response:
        raise TransportLogoutNotSupportedError()

    @staticmethod
    @abstractmethod
    def get_openapi_login_responses_success() -> (
        OpenAPIResponseType
    ): ...  # pragma: no cover


class BearerTransport(BaseBearerTransport[str], Transport):
    async def get_login_response(self, token: str) -> Response:
        bearer_response = BearerResponse(access_token=token, token_type="bearer")
        return JSONResponse(model_dump(bearer_response))

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


class BearerResponseRefresh(BearerResponse):
    refresh_token: str


class BearerTransportRefresh(BaseBearerTransport, TransportRefresh):
    async def get_login_response(
        self,
        token: AccessRefreshToken,
    ) -> Response:
        bearer_response = BearerResponseRefresh(
            access_token=token[0],
            refresh_token=token[1],
            token_type="bearer",
        )
        return JSONResponse(model_dump(bearer_response))

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponseRefresh,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
                            "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
                            "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
                            "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
                            "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
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
    def get_openapi_refresh_responses_success() -> OpenAPIResponseType:
        return BearerTransportRefresh.get_openapi_login_responses_success()

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}
