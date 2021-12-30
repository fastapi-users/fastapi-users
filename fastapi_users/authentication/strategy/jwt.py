from typing import Generic, List, Optional

import jwt
from pydantic import UUID4

from fastapi_users import models
from fastapi_users.authentication.strategy.base import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager, UserNotExists


class JWTStrategy(Strategy, Generic[models.UC, models.UD]):
    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int,
        token_audience: List[str] = ["fastapi-users:auth"],
    ):
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.token_audience = token_audience

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UC, models.UD]
    ) -> Optional[models.UD]:
        if token is None:
            return None

        try:
            data = decode_jwt(token, self.secret, self.token_audience)
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

    async def write_token(self, user: models.UD) -> str:
        data = {"user_id": str(user.id), "aud": self.token_audience}
        return generate_jwt(data, self.secret, self.lifetime_seconds)

    async def destroy_token(self, token: str, user: models.UD) -> None:
        raise StrategyDestroyNotSupportedError(
            "A JWT can't be invalidated: it's valid until it expires."
        )
