import pytest
from fastapi import HTTPException
from starlette import status
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import UserDB
from fastapi_users.password import get_password_hash

active_user_data = UserDB(
    id="aaa",
    email="king.arthur@camelot.bt",
    hashed_password=get_password_hash("guinevere"),
)

inactive_user_data = UserDB(
    id="bbb",
    email="percival@camelot.bt",
    hashed_password=get_password_hash("angharad"),
    is_active=False,
)


@pytest.fixture
def user() -> UserDB:
    return active_user_data


@pytest.fixture
def inactive_user() -> UserDB:
    return inactive_user_data


class MockUserDatabase(BaseUserDatabase):
    async def get(self, id: str) -> UserDB:
        if id == active_user_data.id:
            return active_user_data
        elif id == inactive_user_data.id:
            return inactive_user_data
        return None

    async def get_by_email(self, email: str) -> UserDB:
        if email == active_user_data.email:
            return active_user_data
        elif email == inactive_user_data.email:
            return inactive_user_data
        return None

    async def create(self, user: UserDB) -> UserDB:
        return user


@pytest.fixture
def mock_user_db() -> MockUserDatabase:
    return MockUserDatabase()


class MockAuthentication(BaseAuthentication):
    async def get_login_response(self, user: UserDB, response: Response):
        return {"token": user.id}

    async def authenticate(self, token: str) -> UserDB:
        user = await self.userDB.get(token)
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user


@pytest.fixture
def mock_authentication(mock_user_db) -> MockAuthentication:
    return MockAuthentication(mock_user_db)
