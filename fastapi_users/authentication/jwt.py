from typing import Any, Generic, List, Optional

import jwt
from fastapi import Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4

from fastapi_users import models
from fastapi_users.authentication.base import BaseAuthentication
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager, UserNotExists


class JWTAuthentication(
    Generic[models.UC, models.UD], BaseAuthentication[str, models.UC, models.UD]
):
    """
    Authentication backend using a JWT in a Bearer header.

    :param secret: Secret used to encode the JWT.
    :param lifetime_seconds: Lifetime duration of the JWT in seconds.
    :param tokenUrl: Path where to get a token.
    :param name: Name of the backend. It will be used to name the login route.
    :param token_audience: List of valid audiences for the JWT.
    """

    scheme: OAuth2PasswordBearer
    token_audience: List[str]
    secret: SecretType
    lifetime_seconds: int

    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int,
        tokenUrl: str = "auth/jwt/login",
        name: str = "jwt",
        token_audience: List[str] = ["fastapi-users:auth"],
    ):
        super().__init__(name, logout=False)
        self.scheme = OAuth2PasswordBearer(tokenUrl, auto_error=False)
        self.secret = secret
        self.token_audience = token_audience
        self.lifetime_seconds = lifetime_seconds

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
        return {"access_token": token, "token_type": "bearer"}

    async def _generate_token(self, user: models.UD) -> str:
        data = {"user_id": str(user.id), "aud": self.token_audience}
        return generate_jwt(data, self.secret, self.lifetime_seconds)
