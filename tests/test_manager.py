from typing import Callable, cast

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from pytest_mock import MockerFixture

from fastapi_users import models
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.manager import (
    InvalidPasswordException,
    InvalidResetPasswordToken,
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from tests.conftest import UserCreate, UserDB, UserDBOAuth, UserManagerMock, UserUpdate


@pytest.fixture
def forgot_password_token(user_manager: UserManagerMock):
    def _forgot_password_token(
        user_id=None, lifetime=user_manager.reset_password_token_lifetime_seconds
    ):
        data = {"aud": user_manager.reset_password_token_audience}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(data, user_manager.reset_password_token_secret, lifetime)

    return _forgot_password_token


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
class TestOAuthCallback:
    async def test_existing_user_with_oauth(
        self, user_manager_oauth: UserManagerMock, user_oauth: UserDBOAuth
    ):
        oauth_account = models.BaseOAuthAccount(
            **user_oauth.oauth_accounts[0].dict(exclude={"id", "access_token"}),
            access_token="UPDATED_TOKEN"
        )
        user = cast(UserDBOAuth, await user_manager_oauth.oauth_callback(oauth_account))

        assert user.id == user_oauth.id
        assert len(user.oauth_accounts) == 2
        assert user.oauth_accounts[0].oauth_name == "service1"
        assert user.oauth_accounts[0].access_token == "UPDATED_TOKEN"
        assert user.oauth_accounts[1].access_token == "TOKEN"
        assert user.oauth_accounts[1].oauth_name == "service2"

        assert user_manager_oauth.on_after_register.called is False

    async def test_existing_user_without_oauth(
        self, user_manager_oauth: UserManagerMock, superuser_oauth: UserDBOAuth
    ):
        oauth_account = models.BaseOAuthAccount(
            oauth_name="service1",
            access_token="TOKEN",
            expires_at=1579000751,
            account_id="superuser_oauth1",
            account_email=superuser_oauth.email,
        )
        user = cast(UserDBOAuth, await user_manager_oauth.oauth_callback(oauth_account))

        assert user.id == superuser_oauth.id
        assert len(user.oauth_accounts) == 1
        assert user.oauth_accounts[0].id == oauth_account.id

        assert user_manager_oauth.on_after_register.called is False

    async def test_new_user(self, user_manager_oauth: UserManagerMock):
        oauth_account = models.BaseOAuthAccount(
            oauth_name="service1",
            access_token="TOKEN",
            expires_at=1579000751,
            account_id="new_user_oauth1",
            account_email="galahad@camelot.bt",
        )
        user = cast(UserDBOAuth, await user_manager_oauth.oauth_callback(oauth_account))

        assert user.email == "galahad@camelot.bt"
        assert len(user.oauth_accounts) == 1
        assert user.oauth_accounts[0].id == oauth_account.id

        assert user_manager_oauth.on_after_register.called is True


@pytest.mark.asyncio
class TestUpdateUser:
    async def test_safe_update(self, user: UserDB, user_manager: UserManagerMock):
        user_update = UserUpdate(first_name="Arthur", is_superuser=True)
        updated_user = await user_manager.update(user_update, user, safe=True)

        assert updated_user.first_name == "Arthur"
        assert updated_user.is_superuser is False

        assert user_manager.on_after_update.called is True

    async def test_unsafe_update(self, user: UserDB, user_manager: UserManagerMock):
        user_update = UserUpdate(first_name="Arthur", is_superuser=True)
        updated_user = await user_manager.update(user_update, user, safe=False)

        assert updated_user.first_name == "Arthur"
        assert updated_user.is_superuser is True

        assert user_manager.on_after_update.called is True


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


@pytest.mark.asyncio
class TestForgotPassword:
    async def test_user_inactive(
        self, user_manager: UserManagerMock, inactive_user: UserDB
    ):
        with pytest.raises(UserInactive):
            await user_manager.forgot_password(inactive_user)
        assert user_manager.on_after_forgot_password.called is False

    async def test_user_active(self, user_manager: UserManagerMock, user: UserDB):
        await user_manager.forgot_password(user)
        assert user_manager.on_after_forgot_password.called is True

        actual_user = user_manager.on_after_forgot_password.call_args[0][0]
        actual_token = user_manager.on_after_forgot_password.call_args[0][1]

        assert actual_user.id == user.id
        decoded_token = decode_jwt(
            actual_token,
            user_manager.reset_password_token_secret,
            audience=[user_manager.reset_password_token_audience],
        )
        assert decoded_token["user_id"] == str(user.id)


@pytest.mark.asyncio
class TestResetPassword:
    async def test_invalid_token(self, user_manager: UserManagerMock):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password("foo", "guinevere")
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    @pytest.mark.parametrize("user_id", [None, "foo"])
    async def test_valid_token_bad_payload(
        self, user_id: str, user_manager: UserManagerMock, forgot_password_token
    ):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password(
                forgot_password_token(user_id), "guinevere"
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_not_existing_user(
        self, user_manager: UserManagerMock, forgot_password_token
    ):
        with pytest.raises(UserNotExists):
            await user_manager.reset_password(
                forgot_password_token("d35d213e-f3d8-4f08-954a-7e0d1bea286f"),
                "guinevere",
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_inactive_user(
        self,
        inactive_user: UserDB,
        user_manager: UserManagerMock,
        forgot_password_token,
    ):
        with pytest.raises(UserInactive):
            await user_manager.reset_password(
                forgot_password_token(inactive_user.id),
                "guinevere",
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_invalid_password(
        self, user: UserDB, user_manager: UserManagerMock, forgot_password_token
    ):
        with pytest.raises(InvalidPasswordException):
            await user_manager.reset_password(
                forgot_password_token(user.id),
                "h",
            )
        assert user_manager.on_after_reset_password.called is False

    async def test_valid_user_password(
        self, user: UserDB, user_manager: UserManagerMock, forgot_password_token
    ):
        await user_manager.reset_password(forgot_password_token(user.id), "holygrail")

        assert user_manager._update.called is True
        update_dict = user_manager._update.call_args[0][1]
        assert update_dict == {"password": "holygrail"}

        assert user_manager.on_after_reset_password.called is True
        actual_user = user_manager.on_after_reset_password.call_args[0][0]
        assert actual_user.id == user.id


@pytest.mark.asyncio
class TestAuthenticate:
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
