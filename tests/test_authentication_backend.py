from typing import Callable, Generic, Optional, Type, cast

import pytest
from fastapi import Response

from fastapi_users import models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    Strategy,
)
from fastapi_users.authentication.strategy import StrategyDestroyNotSupportedError
from fastapi_users.authentication.transport.base import Transport
from fastapi_users.manager import BaseUserManager
from tests.conftest import MockStrategy, MockTransport, UserModel


class MockTransportLogoutNotSupported(BearerTransport):
    pass


class MockStrategyDestroyNotSupported(Strategy, Generic[models.UP]):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        return None

    async def write_token(self, user: models.UP) -> str:
        return "TOKEN"

    async def destroy_token(self, token: str, user: models.UP) -> None:
        raise StrategyDestroyNotSupportedError


@pytest.fixture(params=[MockTransport, MockTransportLogoutNotSupported])
def transport(request) -> Transport:
    transport_class: Type[BearerTransport] = request.param
    return transport_class(tokenUrl="/login")


@pytest.fixture(params=[MockStrategy, MockStrategyDestroyNotSupported])
def get_strategy(request) -> Callable[..., Strategy]:
    strategy_class: Type[Strategy] = request.param
    return lambda: strategy_class()


@pytest.fixture
def backend(
    transport: Transport, get_strategy: Callable[..., Strategy]
) -> AuthenticationBackend:
    return AuthenticationBackend(
        name="mock", transport=transport, get_strategy=get_strategy
    )


@pytest.mark.asyncio
@pytest.mark.authentication
async def test_logout(backend: AuthenticationBackend, user: UserModel):
    strategy = cast(Strategy, backend.get_strategy())
    result = await backend.logout(strategy, user, "TOKEN", Response())
    assert result is None
