from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
)

import httpx
import pytest
from fastapi import Depends, FastAPI, Request, status
from fastapi.security.base import SecurityBase

from fastapi_users import models
from fastapi_users.authentication import (
    Authenticator,
    BaseAuthentication,
    DuplicateBackendNamesError,
)
from fastapi_users.manager import BaseUserManager
from tests.conftest import UserDB


class MockSecurityScheme(SecurityBase):
    def __call__(self, request: Request) -> Optional[str]:
        return "mock"


class BackendNone(
    Generic[models.UC, models.UD], BaseAuthentication[str, models.UC, models.UD]
):
    def __init__(self, name="none"):
        super().__init__(name, logout=False)
        self.scheme = MockSecurityScheme()

    async def __call__(
        self,
        credentials: Optional[str],
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Optional[models.UD]:
        return None

    @staticmethod
    def get_openapi_login_responses_success() -> Dict[str, Any]:
        return {}

    @staticmethod
    def get_openapi_logout_responses_success() -> Dict[str, Any]:
        return {}


class BackendUser(
    Generic[models.UC, models.UD], BaseAuthentication[str, models.UC, models.UD]
):
    def __init__(self, user: models.UD, name="user"):
        super().__init__(name, logout=False)
        self.scheme = MockSecurityScheme()
        self.user = user

    async def __call__(
        self,
        credentials: Optional[str],
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Optional[models.UD]:
        return self.user

    @staticmethod
    def get_openapi_login_responses_success() -> Dict[str, Any]:
        return {}

    @staticmethod
    def get_openapi_logout_responses_success() -> Dict[str, Any]:
        return {}


@pytest.fixture
@pytest.mark.asyncio
def get_test_auth_client(get_user_manager, get_test_client):
    async def _get_test_auth_client(
        backends: List[BaseAuthentication],
        get_enabled_backends: Optional[
            Callable[..., Sequence[BaseAuthentication]]
        ] = None,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        app = FastAPI()
        authenticator = Authenticator(backends, get_user_manager)

        @app.get("/test-current-user")
        def test_current_user(
            user: UserDB = Depends(
                authenticator.current_user(get_enabled_backends=get_enabled_backends)
            ),
        ):
            return user

        @app.get("/test-current-active-user")
        def test_current_active_user(
            user: UserDB = Depends(
                authenticator.current_user(
                    active=True, get_enabled_backends=get_enabled_backends
                )
            ),
        ):
            return user

        @app.get("/test-current-superuser")
        def test_current_superuser(
            user: UserDB = Depends(
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
async def test_authenticator(get_test_auth_client, user):
    async for client in get_test_auth_client([BackendNone(), BackendUser(user)]):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticator_none(get_test_auth_client):
    async for client in get_test_auth_client(
        [BackendNone(), BackendNone(name="none-bis")]
    ):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticator_none_enabled(get_test_auth_client, user):
    backend_none = BackendNone()
    backend_user = BackendUser(user)

    async def get_enabled_backends():
        return [backend_none]

    async for client in get_test_auth_client(
        [backend_none, backend_user], get_enabled_backends
    ):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_authenticators_with_same_name(get_test_auth_client):
    with pytest.raises(DuplicateBackendNamesError):
        async for _ in get_test_auth_client([BackendNone(), BackendNone()]):
            pass
