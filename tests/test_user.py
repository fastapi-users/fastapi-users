import pytest

from fastapi_users.user import (
    CreateUserProtocol,
    UserAlreadyExists,
    UserAlreadyVerified,
    VerifyUserProtocol,
    get_create_user,
    get_verify_user,
)
from tests.conftest import UserCreate, UserDB


@pytest.fixture
def create_user(
    mock_user_db,
) -> CreateUserProtocol:
    return get_create_user(mock_user_db, UserDB)


@pytest.mark.asyncio
class TestCreateUser:
    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(self, email, create_user):
        user = UserCreate(email=email, password="guinevere")
        with pytest.raises(UserAlreadyExists):
            await create_user(user)

    @pytest.mark.parametrize("email", ["lancelot@camelot.bt", "Lancelot@camelot.bt"])
    async def test_regular_user(self, email, create_user):
        user = UserCreate(email=email, password="guinevere")
        created_user = await create_user(user)
        assert type(created_user) == UserDB

    @pytest.mark.parametrize("safe,result", [(True, False), (False, True)])
    async def test_superuser(self, create_user, safe, result):
        user = UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_superuser=True
        )
        created_user = await create_user(user, safe)
        assert type(created_user) == UserDB
        assert created_user.is_superuser is result

    @pytest.mark.parametrize("safe,result", [(True, True), (False, False)])
    async def test_is_active(self, create_user, safe, result):
        user = UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_active=False
        )
        created_user = await create_user(user, safe)
        assert type(created_user) == UserDB
        assert created_user.is_active is result


@pytest.fixture
def verify_user(
    mock_user_db,
) -> VerifyUserProtocol:
    return get_verify_user(mock_user_db)


@pytest.mark.asyncio
class TestVerifyUser:
    async def test_already_verified_user(self, verify_user, verified_user):
        with pytest.raises(UserAlreadyVerified):
            await verify_user(verified_user)

    async def test_non_verified_user(self, verify_user, user):
        user = await verify_user(user)
        assert user.is_verified
