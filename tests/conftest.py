from typing import Optional

import pytest
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
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


@pytest.fixture
def user() -> BaseUserDB:
    return active_user_data


@pytest.fixture
def inactive_user() -> BaseUserDB:
    return inactive_user_data


class MockUserDatabase(BaseUserDatabase):
    async def get(self, id: str) -> Optional[BaseUserDB]:
        if id == active_user_data.id:
            return active_user_data
        elif id == inactive_user_data.id:
            return inactive_user_data
        return None

    async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
        if email == active_user_data.email:
            return active_user_data
        elif email == inactive_user_data.email:
            return inactive_user_data
        return None

    async def create(self, user: BaseUserDB) -> BaseUserDB:
        return user


@pytest.fixture
def mock_user_db() -> MockUserDatabase:
    return MockUserDatabase()


class MockAuthentication(BaseAuthentication):
    async def get_login_response(self, user: BaseUserDB, response: Response):
        return {"token": user.id}

    def get_authentication_method(self, user_db: BaseUserDatabase):
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

        async def authentication_method(token: str = Depends(oauth2_scheme)):
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            user = await user_db.get(token)
            if user is None or not user.is_active:
                raise credentials_exception
            return user

        return authentication_method


@pytest.fixture
def mock_authentication() -> MockAuthentication:
    return MockAuthentication()
