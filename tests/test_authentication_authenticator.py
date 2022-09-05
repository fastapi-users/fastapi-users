from typing import AsyncGenerator, Generic, List, Optional, Sequence, Tuple

import httpx
import pytest
from fastapi import Depends, FastAPI, Request, status
from fastapi.security.base import SecurityBase

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, Authenticator
from fastapi_users.authentication.authenticator import DuplicateBackendNamesError
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.authentication.token import TokenData, UserTokenData
from fastapi_users.authentication.transport import Transport
from fastapi_users.manager import BaseUserManager
from fastapi_users.types import DependencyCallable
from tests.conftest import IDType, User, UserModel


class MockSecurityScheme(SecurityBase):
    def __call__(self, request: Request) -> Optional[str]:
        return "mock"


class MockTransport(Transport):
    scheme: MockSecurityScheme

    def __init__(self):
        self.scheme = MockSecurityScheme()


class NoneStrategy(Strategy):
    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[UserTokenData[models.UP, models.ID]]:
        return None


class UserStrategy(Strategy, Generic[models.UP, models.ID]):
    def __init__(self, token_data: UserTokenData[models.UP, models.ID]):
        self.token_data = token_data

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[UserTokenData[models.UP, models.ID]]:
        return self.token_data


@pytest.fixture
def get_backend_none():
    def _get_backend_none(name: str = "none"):
        return AuthenticationBackend(
            name=name, transport=MockTransport(), get_strategy=lambda: NoneStrategy()
        )

    return _get_backend_none


@pytest.fixture
def get_backend_user(token_data: UserTokenData[UserModel, IDType]):
    def _get_backend_user(name: str = "user"):
        return AuthenticationBackend(
            name=name,
            transport=MockTransport(),
            get_strategy=lambda: UserStrategy(token_data),
        )

    return _get_backend_user


@pytest.fixture(params=[False])
def require_active(request: pytest.FixtureRequest) -> bool:
    return getattr(request, "param")


@pytest.fixture(params=[False])
def require_superuser(request: pytest.FixtureRequest) -> bool:
    return getattr(request, "param")


@pytest.fixture
@pytest.mark.asyncio
def get_test_auth_client(
    get_user_manager, get_test_client, require_active: bool, require_superuser: bool
):
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
                authenticator.current_user(
                    active=require_active,
                    superuser=require_superuser,
                    get_enabled_backends=get_enabled_backends,
                )
            ),
        ):
            return user

        @app.get("/test-current-user-token", response_model=User)
        def test_current_token(
            user_token: Tuple[UserModel, str] = Depends(
                authenticator.current_user_token(
                    active=require_active,
                    superuser=require_superuser,
                    get_enabled_backends=get_enabled_backends,
                )
            ),
        ):
            user, token = user_token
            assert token
            return user

        @app.get("/test-current-token", response_model=TokenData)
        def test_current_token(
            token_data: UserTokenData[UserModel, IDType] = Depends(
                authenticator.current_token(
                    active=require_active,
                    superuser=require_superuser,
                    get_enabled_backends=get_enabled_backends,
                )
            ),
        ):
            return TokenData(**token_data.dict())

        async for client in get_test_client(app):
            yield client

    return _get_test_auth_client


@pytest.mark.authentication
@pytest.mark.asyncio
@pytest.mark.parametrize("require_active", [False], indirect=True)
@pytest.mark.parametrize("require_superuser", [False], indirect=True)
@pytest.mark.parametrize(
    "path",
    [
        "/test-current-user",
        "/test-current-user-token",
        "/test-current-token",
    ],
)
async def test_authenticator(
    get_test_auth_client, get_backend_none, get_backend_user, path: str
):
    async for client in get_test_auth_client([get_backend_none(), get_backend_user()]):
        response = await client.get(path)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.authentication
@pytest.mark.asyncio
@pytest.mark.parametrize("require_active", [False], indirect=True)
@pytest.mark.parametrize("require_superuser", [False], indirect=True)
@pytest.mark.parametrize(
    "path",
    [
        "/test-current-user",
        "/test-current-user-token",
        "/test-current-token",
    ],
)
async def test_authenticator_none(get_test_auth_client, get_backend_none, path: str):
    async for client in get_test_auth_client(
        [get_backend_none(), get_backend_none(name="none-bis")]
    ):
        response = await client.get(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
@pytest.mark.asyncio
@pytest.mark.parametrize("require_active", [False], indirect=True)
@pytest.mark.parametrize("require_superuser", [False], indirect=True)
@pytest.mark.parametrize(
    "path",
    [
        "/test-current-user",
        "/test-current-user-token",
        "/test-current-token",
    ],
)
async def test_authenticator_none_enabled(
    get_test_auth_client, get_backend_none, get_backend_user, path: str
):
    backend_none = get_backend_none()
    backend_user = get_backend_user()

    async def get_enabled_backends():
        return [backend_none]

    async for client in get_test_auth_client(
        [backend_none, backend_user], get_enabled_backends
    ):
        response = await client.get(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticators_with_same_name(get_test_auth_client, get_backend_none):
    with pytest.raises(DuplicateBackendNamesError):
        async for _ in get_test_auth_client([get_backend_none(), get_backend_none()]):
            pass
