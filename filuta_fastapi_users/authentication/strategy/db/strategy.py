import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional

from filuta_fastapi_users import exceptions, models
from filuta_fastapi_users.authentication.strategy.base import Strategy
from filuta_fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase
from filuta_fastapi_users.authentication.strategy.db.models import AP
from filuta_fastapi_users.manager import BaseUserManager


def packToJson(data):
    return json.dumps(data)

def unpackFromJson(str):
    return json.loads(str)

class DatabaseStrategy(
    Strategy[models.UP, models.ID], Generic[models.UP, models.ID, AP]
):
    def __init__(
        self, database: AccessTokenDatabase[AP], lifetime_seconds: Optional[int] = None
    ):
        self.database = database
        self.lifetime_seconds = lifetime_seconds

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )

        access_token = await self.database.get_by_token(token, max_age)
        if access_token is None:
            return None

        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def get_token_record(
        self, token: Optional[str]
    ) -> Optional[models.UP]:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )

        access_token = await self.database.get_by_token(token, max_age)
        return access_token

    async def write_token(self, user: models.UP) -> str:
        access_token_dict = self._create_access_token_dict(user)
        access_token = await self.database.create(access_token_dict)
        return access_token

    async def destroy_token(self, token: str, user: models.UP) -> None:
        access_token = await self.database.get_by_token(token)
        if access_token is not None:
            await self.database.delete(access_token)

    def _create_access_token_dict(self, user: models.UP) -> Dict[str, Any]:
        token = secrets.token_urlsafe()
        return {"token": token, "user_id": user.id, "scopes": "none", "mfa_scopes": {"email": 0}}
