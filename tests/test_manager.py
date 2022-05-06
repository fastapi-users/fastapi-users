from typing import Callable

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4
from pytest_mock import MockerFixture

from fastapi_users.exceptions import (
    InvalidID,
    InvalidPasswordException,
    InvalidResetPasswordToken,
    InvalidVerifyToken,
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.manager import IntegerIDMixin
from tests.conftest import (
    UserCreate,
    UserManagerMock,
    UserModel,
    UserOAuthModel,
    UserUpdate,
)


@pytest.fixture
def verify_token(user_manager: UserManagerMock[UserModel]):
    def _verify_token(
        user_id=None,
        email=None,
        lifetime=user_manager.verification_token_lifetime_seconds,
    ):
        data = {"aud": user_manager.verification_token_audience}
        if user_id is not None:
            data["user_id"] = str(user_id)
        if email is not None:
            data["email"] = email
        return generate_jwt(data, user_manager.verification_token_secret, lifetime)

    return _verify_token


@pytest.fixture
def forgot_password_token(user_manager: UserManagerMock[UserModel]):
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
@pytest.mark.manager
class TestGet:
    async def test_not_existing_user(self, user_manager: UserManagerMock[UserModel]):
        with pytest.raises(UserNotExists):
            await user_manager.get(UUID4("d35d213e-f3d8-4f08-954a-7e0d1bea286f"))

    async def test_existing_user(
        self, user_manager: UserManagerMock[UserModel], user: UserModel
    ):
        retrieved_user = await user_manager.get(user.id)
        assert retrieved_user.id == user.id


@pytest.mark.asyncio
@pytest.mark.manager
class TestGetByEmail:
    async def test_not_existing_user(self, user_manager: UserManagerMock[UserModel]):
        with pytest.raises(UserNotExists):
            await user_manager.get_by_email("lancelot@camelot.bt")

    async def test_existing_user(
        self, user_manager: UserManagerMock[UserModel], user: UserModel
    ):
        retrieved_user = await user_manager.get_by_email(user.email)
        assert retrieved_user.id == user.id


@pytest.mark.asyncio
@pytest.mark.manager
class TestGetByOAuthAccount:
    async def test_not_existing_user(
        self, user_manager_oauth: UserManagerMock[UserModel]
    ):
        with pytest.raises(UserNotExists):
            await user_manager_oauth.get_by_oauth_account("service1", "foo")

    async def test_existing_user(
        self, user_manager_oauth: UserManagerMock[UserModel], user_oauth: UserOAuthModel
    ):
        oauth_account = user_oauth.oauth_accounts[0]
        retrieved_user = await user_manager_oauth.get_by_oauth_account(
            oauth_account.oauth_name, oauth_account.account_id
        )
        assert retrieved_user.id == user_oauth.id


@pytest.mark.asyncio
@pytest.mark.manager
class TestCreateUser:
    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(
        self, email: str, user_manager: UserManagerMock[UserModel]
    ):
        user = UserCreate(email=email, password="guinevere")
        with pytest.raises(UserAlreadyExists):
            await user_manager.create(user)
        assert user_manager.on_after_register.called is False

    @pytest.mark.parametrize("email", ["lancelot@camelot.bt", "Lancelot@camelot.bt"])
    async def test_regular_user(
        self, email: str, user_manager: UserManagerMock[UserModel]
    ):
        user = UserCreate(email=email, password="guinevere")
        created_user = await user_manager.create(user)
        assert type(created_user) == UserModel

        assert user_manager.on_after_register.called is True

    @pytest.mark.parametrize("safe,result", [(True, False), (False, True)])
    async def test_superuser(
        self, user_manager: UserManagerMock[UserModel], safe: bool, result: bool
    ):
        user = UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_superuser=True
        )
        created_user = await user_manager.create(user, safe)
        assert type(created_user) == UserModel
        assert created_user.is_superuser is result

        assert user_manager.on_after_register.called is True

    @pytest.mark.parametrize("safe,result", [(True, True), (False, False)])
    async def test_is_active(
        self, user_manager: UserManagerMock[UserModel], safe: bool, result: bool
    ):
        user = UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_active=False
        )
        created_user = await user_manager.create(user, safe)
        assert type(created_user) == UserModel
        assert created_user.is_active is result

        assert user_manager.on_after_register.called is True


@pytest.mark.asyncio
@pytest.mark.manager
class TestOAuthCallback:
    async def test_existing_user_with_oauth(
        self,
        user_manager_oauth: UserManagerMock[UserOAuthModel],
        user_oauth: UserOAuthModel,
    ):
        oauth_account = user_oauth.oauth_accounts[0]

        user = await user_manager_oauth.oauth_callback(
            oauth_account.oauth_name,
            "UPDATED_TOKEN",
            oauth_account.account_id,
            oauth_account.account_email,
        )

        assert user.id == user_oauth.id
        assert len(user.oauth_accounts) == 2
        assert user.oauth_accounts[0].id == oauth_account.id
        assert user.oauth_accounts[0].oauth_name == "service1"
        assert user.oauth_accounts[0].access_token == "UPDATED_TOKEN"
        assert user.oauth_accounts[1].access_token == "TOKEN"
        assert user.oauth_accounts[1].oauth_name == "service2"

        assert user_manager_oauth.on_after_register.called is False

    async def test_existing_user_without_oauth(
        self,
        user_manager_oauth: UserManagerMock[UserOAuthModel],
        superuser_oauth: UserOAuthModel,
    ):
        user = await user_manager_oauth.oauth_callback(
            "service1", "TOKEN", "superuser_oauth1", superuser_oauth.email, 1579000751
        )

        assert user.id == superuser_oauth.id
        assert len(user.oauth_accounts) == 1
        assert user.oauth_accounts[0].id is not None

        assert user_manager_oauth.on_after_register.called is False

    async def test_new_user(self, user_manager_oauth: UserManagerMock[UserOAuthModel]):
        user = await user_manager_oauth.oauth_callback(
            "service1", "TOKEN", "new_user_oauth1", "galahad@camelot.bt", 1579000751
        )

        assert user.email == "galahad@camelot.bt"
        assert len(user.oauth_accounts) == 1
        assert user.oauth_accounts[0].id is not None

        assert user_manager_oauth.on_after_register.called is True


@pytest.mark.asyncio
@pytest.mark.manager
class TestRequestVerifyUser:
    async def test_user_inactive(
        self, user_manager: UserManagerMock[UserModel], inactive_user: UserModel
    ):
        with pytest.raises(UserInactive):
            await user_manager.request_verify(inactive_user)

    async def test_user_verified(
        self, user_manager: UserManagerMock[UserModel], verified_user: UserModel
    ):
        with pytest.raises(UserAlreadyVerified):
            await user_manager.request_verify(verified_user)

    async def test_user_active_not_verified(
        self, user_manager: UserManagerMock[UserModel], user: UserModel
    ):
        await user_manager.request_verify(user)
        assert user_manager.on_after_request_verify.called is True

        actual_user = user_manager.on_after_request_verify.call_args[0][0]
        actual_token = user_manager.on_after_request_verify.call_args[0][1]

        assert actual_user.id == user.id
        decoded_token = decode_jwt(
            actual_token,
            user_manager.verification_token_secret,
            audience=[user_manager.verification_token_audience],
        )
        assert decoded_token["user_id"] == str(user.id)
        assert decoded_token["email"] == str(user.email)


@pytest.mark.asyncio
@pytest.mark.manager
class TestVerifyUser:
    async def test_invalid_token(self, user_manager: UserManagerMock[UserModel]):
        with pytest.raises(InvalidVerifyToken):
            await user_manager.verify("foo")

    async def test_token_expired(
        self, user_manager: UserManagerMock[UserModel], user: UserModel, verify_token
    ):
        with pytest.raises(InvalidVerifyToken):
            token = verify_token(user_id=user.id, email=user.email, lifetime=-1)
            await user_manager.verify(token)

    async def test_missing_user_id(
        self, user_manager: UserManagerMock[UserModel], user: UserModel, verify_token
    ):
        with pytest.raises(InvalidVerifyToken):
            token = verify_token(email=user.email)
            await user_manager.verify(token)

    async def test_missing_user_email(
        self, user_manager: UserManagerMock[UserModel], user: UserModel, verify_token
    ):
        with pytest.raises(InvalidVerifyToken):
            token = verify_token(user_id=user.id)
            await user_manager.verify(token)

    async def test_invalid_user_id(
        self, user_manager: UserManagerMock[UserModel], user: UserModel, verify_token
    ):
        with pytest.raises(InvalidVerifyToken):
            token = verify_token(user_id="foo", email=user.email)
            await user_manager.verify(token)

    async def test_invalid_email(
        self, user_manager: UserManagerMock[UserModel], user: UserModel, verify_token
    ):
        with pytest.raises(InvalidVerifyToken):
            token = verify_token(user_id=user.id, email="foo")
            await user_manager.verify(token)

    async def test_email_id_mismatch(
        self,
        user_manager: UserManagerMock[UserModel],
        user: UserModel,
        inactive_user: UserModel,
        verify_token,
    ):
        with pytest.raises(InvalidVerifyToken):
            token = verify_token(user_id=user.id, email=inactive_user.email)
            await user_manager.verify(token)

    async def test_verified_user(
        self,
        user_manager: UserManagerMock[UserModel],
        verified_user: UserModel,
        verify_token,
    ):
        with pytest.raises(UserAlreadyVerified):
            token = verify_token(user_id=verified_user.id, email=verified_user.email)
            await user_manager.verify(token)

    async def test_inactive_user(
        self,
        user_manager: UserManagerMock[UserModel],
        inactive_user: UserModel,
        verify_token,
    ):
        token = verify_token(user_id=inactive_user.id, email=inactive_user.email)
        verified_user = await user_manager.verify(token)

        assert verified_user.is_verified is True
        assert verified_user.is_active is False

    async def test_active_user(
        self, user_manager: UserManagerMock[UserModel], user: UserModel, verify_token
    ):
        token = verify_token(user_id=user.id, email=user.email)
        verified_user = await user_manager.verify(token)

        assert verified_user.is_verified is True
        assert verified_user.is_active is True


@pytest.mark.asyncio
@pytest.mark.manager
class TestForgotPassword:
    async def test_user_inactive(
        self, user_manager: UserManagerMock[UserModel], inactive_user: UserModel
    ):
        with pytest.raises(UserInactive):
            await user_manager.forgot_password(inactive_user)
        assert user_manager.on_after_forgot_password.called is False

    async def test_user_active(
        self, user_manager: UserManagerMock[UserModel], user: UserModel
    ):
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
@pytest.mark.manager
class TestResetPassword:
    async def test_invalid_token(self, user_manager: UserManagerMock[UserModel]):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password("foo", "guinevere")
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_token_expired(
        self,
        user_manager: UserManagerMock[UserModel],
        user: UserModel,
        forgot_password_token,
    ):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password(
                forgot_password_token(user.id, lifetime=-1), "guinevere"
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    @pytest.mark.parametrize("user_id", [None, "foo"])
    async def test_valid_token_bad_payload(
        self,
        user_id: str,
        user_manager: UserManagerMock[UserModel],
        forgot_password_token,
    ):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password(
                forgot_password_token(user_id), "guinevere"
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_not_existing_user(
        self, user_manager: UserManagerMock[UserModel], forgot_password_token
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
        inactive_user: UserModel,
        user_manager: UserManagerMock[UserModel],
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
        self,
        user: UserModel,
        user_manager: UserManagerMock[UserModel],
        forgot_password_token,
    ):
        with pytest.raises(InvalidPasswordException):
            await user_manager.reset_password(
                forgot_password_token(user.id),
                "h",
            )
        assert user_manager.on_after_reset_password.called is False

    async def test_valid_user_password(
        self,
        user: UserModel,
        user_manager: UserManagerMock[UserModel],
        forgot_password_token,
    ):
        await user_manager.reset_password(forgot_password_token(user.id), "holygrail")

        assert user_manager._update.called is True
        update_dict = user_manager._update.call_args[0][1]
        assert update_dict == {"password": "holygrail"}

        assert user_manager.on_after_reset_password.called is True
        actual_user = user_manager.on_after_reset_password.call_args[0][0]
        assert actual_user.id == user.id


@pytest.mark.asyncio
@pytest.mark.manager
class TestUpdateUser:
    async def test_safe_update(
        self, user: UserModel, user_manager: UserManagerMock[UserModel]
    ):
        user_update = UserUpdate(first_name="Arthur", is_superuser=True)
        updated_user = await user_manager.update(user_update, user, safe=True)

        assert updated_user.first_name == "Arthur"
        assert updated_user.is_superuser is False

        assert user_manager.on_after_update.called is True

    async def test_unsafe_update(
        self, user: UserModel, user_manager: UserManagerMock[UserModel]
    ):
        user_update = UserUpdate(first_name="Arthur", is_superuser=True)
        updated_user = await user_manager.update(user_update, user, safe=False)

        assert updated_user.first_name == "Arthur"
        assert updated_user.is_superuser is True

        assert user_manager.on_after_update.called is True

    async def test_password_update_invalid(
        self, user: UserModel, user_manager: UserManagerMock[UserModel]
    ):
        user_update = UserUpdate(password="h")
        with pytest.raises(InvalidPasswordException):
            await user_manager.update(user_update, user, safe=True)

        assert user_manager.on_after_update.called is False

    async def test_password_update_valid(
        self, user: UserModel, user_manager: UserManagerMock[UserModel]
    ):
        old_hashed_password = user.hashed_password
        user_update = UserUpdate(password="holygrail")
        updated_user = await user_manager.update(user_update, user, safe=True)

        assert updated_user.hashed_password != old_hashed_password

        assert user_manager.on_after_update.called is True

    async def test_email_update_already_existing(
        self,
        user: UserModel,
        superuser: UserModel,
        user_manager: UserManagerMock[UserModel],
    ):
        user_update = UserUpdate(email=superuser.email)
        with pytest.raises(UserAlreadyExists):
            await user_manager.update(user_update, user, safe=True)

        assert user_manager.on_after_update.called is False

    async def test_email_update_with_same_email(
        self, user: UserModel, user_manager: UserManagerMock[UserModel]
    ):
        user_update = UserUpdate(email=user.email)
        updated_user = await user_manager.update(user_update, user, safe=True)

        assert updated_user.email == user.email

        assert user_manager.on_after_update.called is True


@pytest.mark.asyncio
@pytest.mark.manager
class TestDelete:
    async def test_delete(
        self, user: UserModel, user_manager: UserManagerMock[UserModel]
    ):
        await user_manager.delete(user)


@pytest.mark.asyncio
@pytest.mark.manager
class TestAuthenticate:
    async def test_unknown_user(
        self,
        create_oauth2_password_request_form: Callable[
            [str, str], OAuth2PasswordRequestForm
        ],
        user_manager: UserManagerMock[UserModel],
    ):
        form = create_oauth2_password_request_form("lancelot@camelot.bt", "guinevere")
        user = await user_manager.authenticate(form)
        assert user is None

    async def test_wrong_password(
        self,
        create_oauth2_password_request_form: Callable[
            [str, str], OAuth2PasswordRequestForm
        ],
        user_manager: UserManagerMock[UserModel],
    ):
        form = create_oauth2_password_request_form("king.arthur@camelot.bt", "percival")
        user = await user_manager.authenticate(form)
        assert user is None

    async def test_valid_credentials(
        self,
        create_oauth2_password_request_form: Callable[
            [str, str], OAuth2PasswordRequestForm
        ],
        user_manager: UserManagerMock[UserModel],
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
        user_manager: UserManagerMock[UserModel],
    ):
        verify_and_update_password_patch = mocker.patch.object(
            user_manager.password_helper, "verify_and_update"
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


def test_integer_id_mixin():
    integer_id_mixin = IntegerIDMixin()

    assert integer_id_mixin.parse_id("123") == 123
    assert integer_id_mixin.parse_id(123) == 123

    with pytest.raises(InvalidID):
        integer_id_mixin.parse_id("123.42")

    with pytest.raises(InvalidID):
        integer_id_mixin.parse_id(123.42)

    with pytest.raises(InvalidID):
        integer_id_mixin.parse_id("abc")
