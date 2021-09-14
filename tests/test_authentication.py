from typing import Optional

import pytest
from fastapi import Request, status
from fastapi.security.base import SecurityBase

from fastapi_users import models
from fastapi_users.authentication import BaseAuthentication, DuplicateBackendNamesError
from fastapi_users.manager import UserManager


class MockSecurityScheme(SecurityBase):
    def __call__(self, request: Request) -> Optional[str]:
        return "mock"


class BackendNone(BaseAuthentication[str]):
    def __init__(self, name="none"):
        super().__init__(name, logout=False)
        self.scheme = MockSecurityScheme()

    async def __call__(
        self, credentials: Optional[str], user_manager: UserManager[models.UD]
    ) -> Optional[models.UD]:
        return None


class BackendUser(BaseAuthentication[str]):
    def __init__(self, user: models.UD, name="user"):
        super().__init__(name, logout=False)
        self.scheme = MockSecurityScheme()
        self.user = user

    async def __call__(
        self, credentials: Optional[str], user_manager: UserManager[models.UD]
    ) -> Optional[models.UD]:
        return self.user


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
async def test_authenticators_with_same_name(get_test_auth_client):
    with pytest.raises(DuplicateBackendNamesError):
        async for client in get_test_auth_client([BackendNone(), BackendNone()]):
            pass
