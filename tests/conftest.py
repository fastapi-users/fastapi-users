import pytest

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import UserDB
from fastapi_users.password import get_password_hash

active_user = UserDB(
    email='king.arthur@camelot.bt',
    hashed_password=get_password_hash('guinevere'),
)

inactive_user = UserDB(
    email='percival@camelot.bt',
    hashed_password=get_password_hash('angharad'),
    is_active=False
)


@pytest.fixture
def user() -> UserDB:
    return active_user


class MockUserDBInterface(BaseUserDatabase):

    async def get_by_email(self, email: str) -> UserDB:
        if email == active_user.email:
            return active_user
        elif email == inactive_user.email:
            return inactive_user
        return None

    async def create(self, user: UserDB) -> UserDB:
        return user


@pytest.fixture
def mock_db_interface() -> MockUserDBInterface:
    return MockUserDBInterface()
