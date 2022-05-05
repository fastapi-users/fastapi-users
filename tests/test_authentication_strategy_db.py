import dataclasses
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import pytest

from fastapi_users.authentication.strategy import (
    AccessTokenDatabase,
    AccessTokenProtocol,
    DatabaseStrategy,
)
from tests.conftest import IDType, UserModel


@dataclasses.dataclass
class AccessTokenModel(AccessTokenProtocol[IDType]):
    token: str
    user_id: uuid.UUID
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    created_at: datetime = dataclasses.field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AccessTokenDatabaseMock(AccessTokenDatabase[AccessTokenModel]):
    store: Dict[str, AccessTokenModel]

    def __init__(self):
        self.store = {}

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AccessTokenModel]:
        try:
            access_token = self.store[token]
            if max_age is not None and access_token.created_at < max_age:
                return None
            return access_token
        except KeyError:
            return None

    async def create(self, create_dict: Dict[str, Any]) -> AccessTokenModel:
        access_token = AccessTokenModel(**create_dict)
        self.store[access_token.token] = access_token
        return access_token

    async def update(
        self, access_token: AccessTokenModel, update_dict: Dict[str, Any]
    ) -> AccessTokenModel:
        for field, value in update_dict.items():
            setattr(access_token, field, value)
        self.store[access_token.token] = access_token
        return access_token

    async def delete(self, access_token: AccessTokenModel) -> None:
        try:
            del self.store[access_token.token]
        except KeyError:
            pass


@pytest.fixture
def access_token_database() -> AccessTokenDatabaseMock:
    return AccessTokenDatabaseMock()


@pytest.fixture
def database_strategy(access_token_database: AccessTokenDatabaseMock):
    return DatabaseStrategy(access_token_database, 3600)


@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(
        self,
        database_strategy: DatabaseStrategy[UserModel, IDType, AccessTokenModel],
        user_manager,
    ):
        authenticated_user = await database_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self,
        database_strategy: DatabaseStrategy[UserModel, IDType, AccessTokenModel],
        user_manager,
    ):
        authenticated_user = await database_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self,
        database_strategy: DatabaseStrategy[UserModel, IDType, AccessTokenModel],
        access_token_database: AccessTokenDatabaseMock,
        user_manager,
    ):
        await access_token_database.create(
            {
                "token": "TOKEN",
                "user_id": uuid.UUID("d35d213e-f3d8-4f08-954a-7e0d1bea286f"),
            }
        )
        authenticated_user = await database_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self,
        database_strategy: DatabaseStrategy[UserModel, IDType, AccessTokenModel],
        access_token_database: AccessTokenDatabaseMock,
        user_manager,
        user: UserModel,
    ):
        await access_token_database.create({"token": "TOKEN", "user_id": user.id})
        authenticated_user = await database_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(
    database_strategy: DatabaseStrategy[UserModel, IDType, AccessTokenModel],
    access_token_database: AccessTokenDatabaseMock,
    user: UserModel,
):
    token = await database_strategy.write_token(user)

    access_token = await access_token_database.get_by_token(token)
    assert access_token is not None
    assert access_token.user_id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(
    database_strategy: DatabaseStrategy[UserModel, IDType, AccessTokenModel],
    access_token_database: AccessTokenDatabaseMock,
    user: UserModel,
):
    await access_token_database.create({"token": "TOKEN", "user_id": user.id})

    await database_strategy.destroy_token("TOKEN", user)

    assert await access_token_database.get_by_token("TOKEN") is None
