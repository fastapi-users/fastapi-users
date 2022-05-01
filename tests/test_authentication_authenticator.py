from typing import AsyncGenerator, Generic, List, Optional, Sequence

import httpx
import pytest
from fastapi import Depends, FastAPI, Request, status
from fastapi.security.base import SecurityBase

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, Authenticator
from fastapi_users.authentication.authenticator import DuplicateBackendNamesError
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.authentication.transport import Transport
from fastapi_users.manager import BaseUserManager
from fastapi_users.types import DependencyCallable
from tests.conftest import User, UserModel


class MockSecurityScheme(SecurityBase):
    def __call__(self, request: Request) -> Optional[str]:
        return "mock"


class MockTransport(Transport):
    scheme: MockSecurityScheme

    def __init__(self):
        self.scheme = MockSecurityScheme()


class NoneStrategy(Strategy):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        return None


class UserStrategy(Strategy, Generic[models.UP]):
    def __init__(self, user: models.UP):
        self.user = user

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        return self.user


@pytest.fixture
def get_backend_none():
    def _get_backend_none(name: str = "none"):
        return AuthenticationBackend(
            name=name, transport=MockTransport(), get_strategy=lambda: NoneStrategy()
        )

    return _get_backend_none


@pytest.fixture
def get_backend_user(user: UserModel):
    def _get_backend_user(name: str = "user"):
        return AuthenticationBackend(
            name=name,
            transport=MockTransport(),
            get_strategy=lambda: UserStrategy(user),
        )

    return _get_backend_user


@pytest.fixture
@pytest.mark.asyncio
def get_test_auth_client(get_user_manager, get_test_client):
    async def _get_test_auth_client(
        backends: List[AuthenticationBackend],
        get_enabled_backends: Optional[
            DependencyCallable[Sequence[AuthenticationBackend]]
        ] = None,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        app = FastAPI()
        authenticator = Authenticator(backends, get_user_manager)

        @app.get("/test-current-user", response_model=User)
        def test_current_user(
            user: UserModel = Depends(
                authenticator.current_user(get_enabled_backends=get_enabled_backends)
            ),
        ):
            return user

        @app.get("/test-current-active-user", response_model=User)
        def test_current_active_user(
            user: UserModel = Depends(
                authenticator.current_user(
                    active=True, get_enabled_backends=get_enabled_backends
                )
            ),
        ):
            return user

        @app.get("/test-current-superuser", response_model=User)
        def test_current_superuser(
            user: UserModel = Depends(
                authenticator.current_user(
                    active=True,
                    superuser=True,
                    get_enabled_backends=get_enabled_backends,
                )
            ),
        ):
            return user

        async for client in get_test_client(app):
            yield client

    return _get_test_auth_client


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticator(get_test_auth_client, get_backend_none, get_backend_user):
    async for client in get_test_auth_client([get_backend_none(), get_backend_user()]):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticator_none(get_test_auth_client, get_backend_none):
    async for client in get_test_auth_client(
        [get_backend_none(), get_backend_none(name="none-bis")]
    ):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticator_none_enabled(
    get_test_auth_client, get_backend_none, get_backend_user
):
    backend_none = get_backend_none()
    backend_user = get_backend_user()

    async def get_enabled_backends():
        return [backend_none]

    async for client in get_test_auth_client(
        [backend_none, backend_user], get_enabled_backends
    ):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticators_with_same_name(get_test_auth_client, get_backend_none):
    with pytest.raises(DuplicateBackendNamesError):
        async for _ in get_test_auth_client([get_backend_none(), get_backend_none()]):
            pass
