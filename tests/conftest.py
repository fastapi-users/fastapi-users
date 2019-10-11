from typing import Optional

import pytest
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.password import get_password_hash

active_user_data = BaseUserDB(
    id="aaa",
    email="king.arthur@camelot.bt",
    hashed_password=get_password_hash("guinevere"),
)

inactive_user_data = BaseUserDB(
    id="bbb",
    email="percival@camelot.bt",
    hashed_password=get_password_hash("angharad"),
    is_active=False,
)

superuser_data = BaseUserDB(
    id="ccc",
    email="merlin@camelot.bt",
    hashed_password=get_password_hash("viviane"),
    is_superuser=True,
)


@pytest.fixture
def user() -> BaseUserDB:
    return active_user_data


@pytest.fixture
def inactive_user() -> BaseUserDB:
    return inactive_user_data


@pytest.fixture
def superuser() -> BaseUserDB:
    return superuser_data


class MockUserDatabase(BaseUserDatabase):
    async def get(self, id: str) -> Optional[BaseUserDB]:
        if id == active_user_data.id:
            return active_user_data
        elif id == inactive_user_data.id:
            return inactive_user_data
        elif id == superuser_data.id:
            return superuser_data
        return None

    async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
        if email == active_user_data.email:
            return active_user_data
        elif email == inactive_user_data.email:
            return inactive_user_data
        elif email == superuser_data.email:
            return superuser_data
        return None

    async def create(self, user: BaseUserDB) -> BaseUserDB:
        return user


@pytest.fixture
def mock_user_db() -> MockUserDatabase:
    return MockUserDatabase()


class MockAuthentication(BaseAuthentication):
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

    async def get_login_response(self, user: BaseUserDB, response: Response):
        return {"token": user.id}

    def get_current_user(self, user_db: BaseUserDatabase):
        async def _get_current_user(token: str = Depends(self.oauth2_scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_user_base(user)

        return _get_current_user

    def get_current_active_user(self, user_db: BaseUserDatabase):
        async def _get_current_active_user(token: str = Depends(self.oauth2_scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_active_user_base(user)

        return _get_current_active_user

    def get_current_superuser(self, user_db: BaseUserDatabase):
        async def _get_current_superuser(token: str = Depends(self.oauth2_scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_superuser_base(user)

        return _get_current_superuser

    def _get_authentication_method(self, user_db: BaseUserDatabase):
        async def authentication_method(token: str = Depends(self.oauth2_scheme)):
            return await user_db.get(token)

        return authentication_method


@pytest.fixture
def mock_authentication() -> MockAuthentication:
    return MockAuthentication()
