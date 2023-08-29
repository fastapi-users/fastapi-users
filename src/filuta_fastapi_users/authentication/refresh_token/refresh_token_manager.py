import secrets
from datetime import UTC, datetime, timedelta
from typing import Generic

from filuta_fastapi_users import models
from filuta_fastapi_users.authentication.strategy.db.adapter import RefreshTokenDatabase
from filuta_fastapi_users.types import DependencyCallable


class RefreshTokenManager(Generic[models.RTP]):
    def __init__(
        self,
        refresh_token_db: RefreshTokenDatabase[models.RTP],
    ) -> None:
        self.refresh_token_db = refresh_token_db

    def generate_refresh_token(self) -> str:
        return secrets.token_urlsafe()

    async def generate_new_token_for_user(self, user: models.UP) -> models.RTP:
        token = self.generate_refresh_token()

        return await self.refresh_token_db.create({"token": token, "user_id": user.id})

    async def find_refresh_token(self, refresh_token: str, lifetime_seconds: int | None = None) -> models.RTP | None:
        max_age = None
        if lifetime_seconds is not None:
            max_age = datetime.now(UTC) - timedelta(seconds=lifetime_seconds)

        return await self.refresh_token_db.get_by_token(refresh_token, max_age)

    async def delete_record(self, item: models.RTP) -> None:
        return await self.refresh_token_db.delete(item)


RefreshTokenManagerDependency = DependencyCallable[RefreshTokenManager[models.RTP]]
