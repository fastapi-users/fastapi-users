from typing import Optional

import pytest
from starlette import status
from starlette.requests import Request

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB


@pytest.fixture()
def auth_backend_none():
    class BackendNone(BaseAuthentication):
        async def __call__(
            self, request: Request, user_db: BaseUserDatabase
        ) -> Optional[BaseUserDB]:
            return None

    return BackendNone()


@pytest.fixture()
def auth_backend_user(user):
    class BackendUser(BaseAuthentication):
        async def __call__(
            self, request: Request, user_db: BaseUserDatabase
        ) -> Optional[BaseUserDB]:
            return user

    return BackendUser()


@pytest.mark.authentication
def test_authenticator(get_test_auth_client, auth_backend_none, auth_backend_user):
    client = get_test_auth_client([auth_backend_none, auth_backend_user])
    response = client.get("/test-current-user")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.authentication
def test_authenticator_none(get_test_auth_client, auth_backend_none):
    client = get_test_auth_client([auth_backend_none, auth_backend_none])
    response = client.get("/test-current-user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
