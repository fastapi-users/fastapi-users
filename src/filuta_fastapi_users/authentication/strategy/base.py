from typing import Any, Generic, Protocol

from filuta_fastapi_users import models
from filuta_fastapi_users.manager import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol, Generic[models.UP, models.ID, models.AP]):
    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models.UP, models.ID],
        authorized: bool = False,
        ignore_expired: bool = False,
    ) -> models.UP | None:
        ...  # pragma: no cover

    async def update_token(self, access_token: models.AP, data: dict[str, Any]) -> models.AP:
        ...  # pragma: no cover

    async def get_token_record_raw(self, token: str | None) -> models.AP | None:
        ...  # pragma: no cover

    async def get_token_record(self, token: str | None) -> models.AP | None:
        ...  # pragma: no cover

    async def insert_token(self, access_token_dict: dict[str, Any]) -> models.AP:
        ...  # pragma: no cover

    async def write_token(self, user: models.UP) -> models.AP:
        ...  # pragma: no cover

    async def destroy_token(self, token: str) -> None:
        ...  # pragma: no cover

    def generate_token(self) -> str:
        ...  # pragma: no cover
