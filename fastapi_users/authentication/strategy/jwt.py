from datetime import datetime, timezone
from typing import Any, List, Optional

import jwt

from fastapi_users import exceptions, models
from fastapi_users.authentication.strategy.base import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.authentication.token import UserTokenData
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt  # type: ignore
from fastapi_users.manager import BaseUserManager


class JWTStrategy(Strategy):
    def __init__(
        self,
        secret: SecretType,
        token_audience: List[str] = ["fastapi-users:auth"],
        algorithm: str = "HS256",
        public_key: Optional[SecretType] = None,
    ):
        self.secret = secret
        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key

    @property
    def encode_key(self) -> SecretType:
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        return self.public_key or self.secret

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, Any],
    ) -> Optional[UserTokenData[models.UP, models.ID]]:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
        except jwt.PyJWTError:
            return None

        if any(x not in data for x in ["sub", "iat", "auth_time"]):
            return None

        user_id = data["sub"]
        try:
            parsed_id = user_manager.parse_id(user_id)
            user = await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

        if "exp" in data:
            expires_at = datetime.fromtimestamp(data["exp"], tz=timezone.utc)
        else:
            expires_at = None

        scope = data["scope"]

        return UserTokenData(
            user=user,
            created_at=datetime.fromtimestamp(data["iat"], tz=timezone.utc),
            expires_at=expires_at,
            last_authenticated=datetime.fromtimestamp(
                data["auth_time"], tz=timezone.utc
            ),
            scopes=set(scope.split(" ")) if scope else set(),
        )

    async def write_token(
        self,
        token_data: UserTokenData[models.UserProtocol[Any], Any],
    ) -> str:
        data = {
            "sub": str(token_data.user.id),
            "aud": self.token_audience,
            "iat": int(token_data.created_at.timestamp()),
            "scope": token_data.scope,
            "auth_time": int(token_data.last_authenticated.timestamp()),
        }
        if token_data.expires_at:
            data["exp"] = int(token_data.expires_at.timestamp())
        return generate_jwt(data, self.encode_key, algorithm=self.algorithm)

    async def destroy_token(
        self,
        token: str,
        user: models.UserProtocol[Any],
    ) -> None:
        raise StrategyDestroyNotSupportedError(
            "A JWT can't be invalidated: it's valid until it expires."
        )
