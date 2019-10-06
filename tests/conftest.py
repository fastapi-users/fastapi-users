import pytest

from fastapi_users.db import UserDBInterface
from fastapi_users.models import UserDB
from fastapi_users.password import get_password_hash

_user = UserDB(
    email='king.arthur@camelot.bt',
    hashed_password=get_password_hash('guinevere'),
)


@pytest.fixture
def user() -> UserDB:
    return _user


class MockUserDBInterface(UserDBInterface):

    async def get_by_email(self, email: str) -> UserDB:
        if email == _user.email:
            return _user
        return None

    async def create(self, user: UserDB) -> UserDB:
        return user


@pytest.fixture
def mock_db_interface() -> MockUserDBInterface:
    return MockUserDBInterface()
