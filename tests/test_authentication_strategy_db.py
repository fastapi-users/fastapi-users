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
from fastapi_users.authentication.token import UserTokenData
from tests.conftest import IDType, UserManager, UserModel


@dataclasses.dataclass
class AccessTokenModel(AccessTokenProtocol[IDType]):
    token: str
    user_id: uuid.UUID
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    created_at: datetime = dataclasses.field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: Optional[datetime] = None
    last_authenticated: datetime = dataclasses.field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    scopes: str = ""


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


def assert_valid_token_model(
    access_token: Optional[AccessTokenModel],
    token_data: UserTokenData[UserModel, IDType],
):
    assert access_token is not None
    assert access_token.user_id == token_data.user.id
    assert access_token.created_at == token_data.created_at
    assert access_token.expires_at == token_data.expires_at
    assert access_token.last_authenticated == token_data.last_authenticated
    assert access_token.scopes == token_data.scope


@pytest.fixture
def access_token_database() -> AccessTokenDatabaseMock:
    return AccessTokenDatabaseMock()


@pytest.fixture
def database_strategy(access_token_database: AccessTokenDatabaseMock):
    return DatabaseStrategy(access_token_database)


@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(
        self,
        database_strategy: DatabaseStrategy[AccessTokenModel],
        user_manager: UserManager,
    ):
        authenticated_user = await database_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self,
        database_strategy: DatabaseStrategy[AccessTokenModel],
        user_manager: UserManager,
    ):
        authenticated_user = await database_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self,
        database_strategy: DatabaseStrategy[AccessTokenModel],
        access_token_database: AccessTokenDatabaseMock,
        user_manager: UserManager,
        token_data: UserTokenData[UserModel, IDType],
    ):
        await access_token_database.create(
            {
                "token": "TOKEN",
                "user_id": uuid.UUID("d35d213e-f3d8-4f08-954a-7e0d1bea286f"),
                "scopes": token_data.scope,
                **token_data.dict(exclude={"user_id", "user", "scopes"}),
            }
        )
        access_token = await database_strategy.read_token("TOKEN", user_manager)
        assert access_token is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("token_expired", [True])
    async def test_expired_token(
        self,
        database_strategy: DatabaseStrategy[AccessTokenModel],
        access_token_database: AccessTokenDatabaseMock,
        user_manager: UserManager,
        token_data: UserTokenData[UserModel, IDType],
    ):
        await access_token_database.create(
            {
                "token": "TOKEN",
                "user_id": token_data.user.id,
                "scopes": token_data.scope,
                **token_data.dict(exclude={"user_id", "user", "scopes"}),
            }
        )
        access_token = await database_strategy.read_token("TOKEN", user_manager)
        assert access_token is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self,
        database_strategy: DatabaseStrategy[AccessTokenModel],
        access_token_database: AccessTokenDatabaseMock,
        user_manager: UserManager,
        token_data: UserTokenData[UserModel, IDType],
    ):
        await access_token_database.create(
            {
                "token": "TOKEN",
                "user_id": token_data.user.id,
                "scopes": token_data.scope,
                **token_data.dict(exclude={"user_id", "user", "scopes"}),
            }
        )
        access_token = await database_strategy.read_token("TOKEN", user_manager)
        assert access_token is not None
        assert access_token.dict() == token_data.dict()


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(
    database_strategy: DatabaseStrategy[AccessTokenModel],
    access_token_database: AccessTokenDatabaseMock,
    token_data: UserTokenData[UserModel, IDType],
):
    token = await database_strategy.write_token(token_data)

    access_token = await access_token_database.get_by_token(token)
    assert_valid_token_model(access_token, token_data)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(
    database_strategy: DatabaseStrategy[AccessTokenModel],
    access_token_database: AccessTokenDatabaseMock,
    user: UserModel,
):
    await access_token_database.create({"token": "TOKEN", "user_id": user.id})

    await database_strategy.destroy_token("TOKEN", user)

    assert await access_token_database.get_by_token("TOKEN") is None
