from typing import Callable

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from pytest_mock import MockerFixture

from fastapi_users.manager import UserAlreadyExists, UserAlreadyVerified
from tests.conftest import UserCreate, UserDB, UserManagerMock


@pytest.fixture
def create_oauth2_password_request_form() -> Callable[
    [str, str], OAuth2PasswordRequestForm
]:
    def _create_oauth2_password_request_form(username, password):
        return OAuth2PasswordRequestForm(username=username, password=password, scope="")

    return _create_oauth2_password_request_form


@pytest.mark.asyncio
class TestCreateUser:
    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(self, email: str, user_manager: UserManagerMock):
        user = UserCreate(email=email, password="guinevere")
        with pytest.raises(UserAlreadyExists):
            await user_manager.create(user)
        assert user_manager.on_after_register.called is False

    @pytest.mark.parametrize("email", ["lancelot@camelot.bt", "Lancelot@camelot.bt"])
    async def test_regular_user(self, email: str, user_manager: UserManagerMock):
        user = UserCreate(email=email, password="guinevere")
        created_user = await user_manager.create(user)
        assert type(created_user) == UserDB

        assert user_manager.on_after_register.called is True

    @pytest.mark.parametrize("safe,result", [(True, False), (False, True)])
    async def test_superuser(
        self, user_manager: UserManagerMock, safe: bool, result: bool
    ):
        user = UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_superuser=True
        )
        created_user = await user_manager.create(user, safe)
        assert type(created_user) == UserDB
        assert created_user.is_superuser is result

        assert user_manager.on_after_register.called is True

    @pytest.mark.parametrize("safe,result", [(True, True), (False, False)])
    async def test_is_active(
        self, user_manager: UserManagerMock, safe: bool, result: bool
    ):
        user = UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_active=False
        )
        created_user = await user_manager.create(user, safe)
        assert type(created_user) == UserDB
        assert created_user.is_active is result

        assert user_manager.on_after_register.called is True


@pytest.mark.asyncio
class TestVerifyUser:
    async def test_already_verified_user(
        self, user_manager: UserManagerMock, verified_user: UserDB
    ):
        with pytest.raises(UserAlreadyVerified):
            await user_manager.verify(verified_user)

    async def test_non_verified_user(self, user_manager: UserManagerMock, user: UserDB):
        user = await user_manager.verify(user)
        assert user.is_verified


@pytest.mark.db
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_unknown_user(
        self,
        create_oauth2_password_request_form: Callable[
            [str, str], OAuth2PasswordRequestForm
        ],
        user_manager: UserManagerMock,
    ):
        form = create_oauth2_password_request_form("lancelot@camelot.bt", "guinevere")
        user = await user_manager.authenticate(form)
        assert user is None

    @pytest.mark.asyncio
    async def test_wrong_password(
        self,
        create_oauth2_password_request_form: Callable[
            [str, str], OAuth2PasswordRequestForm
        ],
        user_manager: UserManagerMock,
    ):
        form = create_oauth2_password_request_form("king.arthur@camelot.bt", "percival")
        user = await user_manager.authenticate(form)
        assert user is None

    @pytest.mark.asyncio
    async def test_valid_credentials(
        self,
        create_oauth2_password_request_form: Callable[
            [str, str], OAuth2PasswordRequestForm
        ],
        user_manager: UserManagerMock,
    ):
        form = create_oauth2_password_request_form(
            "king.arthur@camelot.bt", "guinevere"
        )
        user = await user_manager.authenticate(form)
        assert user is not None
        assert user.email == "king.arthur@camelot.bt"

    @pytest.mark.asyncio
    async def test_upgrade_password_hash(
        self,
        mocker: MockerFixture,
        create_oauth2_password_request_form: Callable[
            [str, str], OAuth2PasswordRequestForm
        ],
        user_manager: UserManagerMock,
    ):
        verify_and_update_password_patch = mocker.patch(
            "fastapi_users.password.verify_and_update_password"
        )
        verify_and_update_password_patch.return_value = (True, "updated_hash")
        update_spy = mocker.spy(user_manager.user_db, "update")

        form = create_oauth2_password_request_form(
            "king.arthur@camelot.bt", "guinevere"
        )
        user = await user_manager.authenticate(form)
        assert user is not None
        assert user.email == "king.arthur@camelot.bt"
        assert update_spy.called is True
