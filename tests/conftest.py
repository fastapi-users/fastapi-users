from typing import Optional

import pytest
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.password import get_password_hash

guinevere_password_hash = get_password_hash("guinevere")
angharad_password_hash = get_password_hash("angharad")
viviane_password_hash = get_password_hash("viviane")


@pytest.fixture
def user() -> BaseUserDB:
    return BaseUserDB(
        id="aaa",
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
    )


@pytest.fixture
def inactive_user() -> BaseUserDB:
    return BaseUserDB(
        id="bbb",
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
    )


@pytest.fixture
def superuser() -> BaseUserDB:
    return BaseUserDB(
        id="ccc",
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
    )


@pytest.fixture
def mock_user_db(user, inactive_user, superuser) -> BaseUserDatabase:
    class MockUserDatabase(BaseUserDatabase):
        async def get(self, id: str) -> Optional[BaseUserDB]:
            if id == user.id:
                return user
            elif id == inactive_user.id:
                return inactive_user
            elif id == superuser.id:
                return superuser
            return None

        async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
            if email == user.email:
                return user
            elif email == inactive_user.email:
                return inactive_user
            elif email == superuser.email:
                return superuser
            return None

        async def create(self, user: BaseUserDB) -> BaseUserDB:
            return user

        async def update(self, user: BaseUserDB) -> BaseUserDB:
            return user

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
