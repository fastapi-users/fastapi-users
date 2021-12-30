import asyncio
from typing import Any, AsyncGenerator, Callable, Generic, Optional, Type, Union
from unittest.mock import MagicMock

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI, Response
from httpx_oauth.oauth2 import OAuth2
from pydantic import UUID4, SecretStr
from pytest_mock import MockerFixture

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.db import BaseUserDatabase
from fastapi_users.jwt import SecretType
from fastapi_users.manager import (
    BaseUserManager,
    InvalidPasswordException,
    UserNotExists,
)
from fastapi_users.models import BaseOAuthAccount, BaseOAuthAccountMixin
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.password import get_password_hash

guinevere_password_hash = get_password_hash("guinevere")
angharad_password_hash = get_password_hash("angharad")
viviane_password_hash = get_password_hash("viviane")
lancelot_password_hash = get_password_hash("lancelot")
excalibur_password_hash = get_password_hash("excalibur")


class User(models.BaseUser):
    first_name: Optional[str]


class UserCreate(models.BaseUserCreate):
    first_name: Optional[str]


class UserUpdate(models.BaseUserUpdate):
    first_name: Optional[str]


class UserDB(User, models.BaseUserDB):
    pass


class UserOAuth(User, BaseOAuthAccountMixin):
    pass


class UserDBOAuth(UserOAuth, UserDB):
    pass


class BaseTestUserManager(
    Generic[models.UC, models.UD], BaseUserManager[models.UC, models.UD]
):
    reset_password_token_secret = "SECRET"
    verification_token_secret = "SECRET"

    async def validate_password(
        self, password: str, user: Union[models.UC, models.UD]
    ) -> None:
        if len(password) < 3:
            raise InvalidPasswordException(
                reason="Password should be at least 3 characters"
            )


class UserManager(BaseTestUserManager[UserCreate, UserDB]):
    user_db_model = UserDB


class UserManagerOAuth(BaseTestUserManager[UserCreate, UserDBOAuth]):
    user_db_model = UserDBOAuth


class UserManagerMock(UserManager):
    get_by_email: MagicMock
    request_verify: MagicMock
    verify: MagicMock
    forgot_password: MagicMock
    reset_password: MagicMock
    on_after_register: MagicMock
    on_after_request_verify: MagicMock
    on_after_verify: MagicMock
    on_after_forgot_password: MagicMock
    on_after_reset_password: MagicMock
    on_after_update: MagicMock
    _update: MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Force the pytest-asyncio loop to be the main one."""
    loop = asyncio.get_event_loop()
    yield loop


AsyncMethodMocker = Callable[..., MagicMock]


@pytest.fixture
def async_method_mocker(mocker: MockerFixture) -> AsyncMethodMocker:
    def _async_method_mocker(
        object: Any,
        method: str,
        return_value: Any = None,
    ) -> MagicMock:
        mock: MagicMock = mocker.MagicMock()

        future: asyncio.Future = asyncio.Future()
        future.set_result(return_value)
        mock.return_value = future
        mock.side_effect = None

        setattr(object, method, mock)

        return mock

    return _async_method_mocker


@pytest.fixture(params=["SECRET", SecretStr("SECRET")])
def secret(request) -> SecretType:
    return request.param


@pytest.fixture
def user() -> UserDB:
    return UserDB(
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
    )


@pytest.fixture
def user_oauth(oauth_account1, oauth_account2) -> UserDBOAuth:
    return UserDBOAuth(
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
        oauth_accounts=[oauth_account1, oauth_account2],
    )


@pytest.fixture
def inactive_user() -> UserDB:
    return UserDB(
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
    )


@pytest.fixture
def inactive_user_oauth(oauth_account3) -> UserDBOAuth:
    return UserDBOAuth(
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
        oauth_accounts=[oauth_account3],
    )


@pytest.fixture
def verified_user() -> UserDB:
    return UserDB(
        email="lake.lady@camelot.bt",
        hashed_password=excalibur_password_hash,
        is_active=True,
        is_verified=True,
    )


@pytest.fixture
def verified_user_oauth(oauth_account4) -> UserDBOAuth:
    return UserDBOAuth(
        email="lake.lady@camelot.bt",
        hashed_password=excalibur_password_hash,
        is_active=False,
        oauth_accounts=[oauth_account4],
    )


@pytest.fixture
def superuser() -> UserDB:
    return UserDB(
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
    )


@pytest.fixture
def superuser_oauth() -> UserDBOAuth:
    return UserDBOAuth(
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        oauth_accounts=[],
    )


@pytest.fixture
def verified_superuser() -> UserDB:
    return UserDB(
        email="the.real.merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        is_verified=True,
    )


@pytest.fixture
def verified_superuser_oauth() -> UserDBOAuth:
    return UserDBOAuth(
        email="the.real.merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        is_verified=True,
        oauth_accounts=[],
    )


@pytest.fixture
def oauth_account1() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        oauth_name="service1",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth1",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account2() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        oauth_name="service2",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth2",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account3() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        oauth_name="service3",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="inactive_user_oauth1",
        account_email="percival@camelot.bt",
    )


@pytest.fixture
def oauth_account4() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        oauth_name="service4",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="verified_user_oauth1",
        account_email="lake.lady@camelot.bt",
    )


@pytest.fixture
def oauth_account5() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        oauth_name="service5",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="verified_superuser_oauth1",
        account_email="the.real.merlin@camelot.bt",
    )


@pytest.fixture
def mock_user_db(
    user, verified_user, inactive_user, superuser, verified_superuser
) -> BaseUserDatabase:
    class MockUserDatabase(BaseUserDatabase[UserDB]):
        async def get(self, id: UUID4) -> Optional[UserDB]:
            if id == user.id:
                return user
            if id == verified_user.id:
                return verified_user
            if id == inactive_user.id:
                return inactive_user
            if id == superuser.id:
                return superuser
            if id == verified_superuser.id:
                return verified_superuser
            return None

        async def get_by_email(self, email: str) -> Optional[UserDB]:
            lower_email = email.lower()
            if lower_email == user.email.lower():
                return user
            if lower_email == verified_user.email.lower():
                return verified_user
            if lower_email == inactive_user.email.lower():
                return inactive_user
            if lower_email == superuser.email.lower():
                return superuser
            if lower_email == verified_superuser.email.lower():
                return verified_superuser
            return None

        async def create(self, user: UserDB) -> UserDB:
            return user

        async def update(self, user: UserDB) -> UserDB:
            return user

        async def delete(self, user: UserDB) -> None:
            pass

    return MockUserDatabase(UserDB)


@pytest.fixture
def mock_user_db_oauth(
    user_oauth,
    verified_user_oauth,
    inactive_user_oauth,
    superuser_oauth,
    verified_superuser_oauth,
) -> BaseUserDatabase:
    class MockUserDatabase(BaseUserDatabase[UserDBOAuth]):
        async def get(self, id: UUID4) -> Optional[UserDBOAuth]:
            if id == user_oauth.id:
                return user_oauth
            if id == verified_user_oauth.id:
                return verified_user_oauth
            if id == inactive_user_oauth.id:
                return inactive_user_oauth
            if id == superuser_oauth.id:
                return superuser_oauth
            if id == verified_superuser_oauth.id:
                return verified_superuser_oauth
            return None

        async def get_by_email(self, email: str) -> Optional[UserDBOAuth]:
            lower_email = email.lower()
            if lower_email == user_oauth.email.lower():
                return user_oauth
            if lower_email == verified_user_oauth.email.lower():
                return verified_user_oauth
            if lower_email == inactive_user_oauth.email.lower():
                return inactive_user_oauth
            if lower_email == superuser_oauth.email.lower():
                return superuser_oauth
            if lower_email == verified_superuser_oauth.email.lower():
                return verified_superuser_oauth
            return None

        async def get_by_oauth_account(
            self, oauth: str, account_id: str
        ) -> Optional[UserDBOAuth]:
            user_oauth_account = user_oauth.oauth_accounts[0]
            if (
                user_oauth_account.oauth_name == oauth
                and user_oauth_account.account_id == account_id
            ):
                return user_oauth

            inactive_user_oauth_account = inactive_user_oauth.oauth_accounts[0]
            if (
                inactive_user_oauth_account.oauth_name == oauth
                and inactive_user_oauth_account.account_id == account_id
            ):
                return inactive_user_oauth
            return None

        async def create(self, user: UserDBOAuth) -> UserDBOAuth:
            return user_oauth

        async def update(self, user: UserDBOAuth) -> UserDBOAuth:
            return user_oauth

        async def delete(self, user: UserDBOAuth) -> None:
            pass

    return MockUserDatabase(UserDBOAuth)


@pytest.fixture
def make_user_manager(mocker: MockerFixture):
    def _make_user_manager(user_manager_class: Type[BaseTestUserManager], mock_user_db):
        user_manager = user_manager_class(mock_user_db)
        mocker.spy(user_manager, "get_by_email")
        mocker.spy(user_manager, "request_verify")
        mocker.spy(user_manager, "verify")
        mocker.spy(user_manager, "forgot_password")
        mocker.spy(user_manager, "reset_password")
        mocker.spy(user_manager, "on_after_register")
        mocker.spy(user_manager, "on_after_request_verify")
        mocker.spy(user_manager, "on_after_verify")
        mocker.spy(user_manager, "on_after_forgot_password")
        mocker.spy(user_manager, "on_after_reset_password")
        mocker.spy(user_manager, "on_after_update")
        mocker.spy(user_manager, "_update")
        return user_manager

    return _make_user_manager


@pytest.fixture
def user_manager(make_user_manager, mock_user_db):
    return make_user_manager(UserManager, mock_user_db)


@pytest.fixture
def user_manager_oauth(make_user_manager, mock_user_db_oauth):
    return make_user_manager(UserManagerOAuth, mock_user_db_oauth)


@pytest.fixture
def get_user_manager(user_manager):
    def _get_user_manager():
        return user_manager

    return _get_user_manager


@pytest.fixture
def get_user_manager_oauth(user_manager_oauth):
    def _get_user_manager_oauth():
        return user_manager_oauth

    return _get_user_manager_oauth


class MockTransport(BearerTransport):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl)

    async def get_logout_response(self, response: Response) -> Any:
        return None

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}


class MockStrategy(Strategy[UserCreate, UserDB]):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[UserCreate, UserDB]
    ) -> Optional[UserDB]:
        if token is not None:
            try:
                token_uuid = UUID4(token)
                return await user_manager.get(token_uuid)
            except ValueError:
                return None
            except UserNotExists:
                return None
        return None

    async def write_token(self, user: models.UD) -> str:
        return str(user.id)

    async def destroy_token(self, token: str, user: models.UD) -> None:
        return None


def get_mock_authentication(name: str):
    return AuthenticationBackend(
        name=name,
        transport=MockTransport(tokenUrl="/login"),
        get_strategy=lambda: MockStrategy(),
    )


@pytest.fixture
def mock_authentication():
    return get_mock_authentication(name="mock")


@pytest.fixture
def get_test_client():
    async def _get_test_client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
        async with LifespanManager(app):
            async with httpx.AsyncClient(
                app=app, base_url="http://app.io"
            ) as test_client:
                yield test_client

    return _get_test_client


@pytest.fixture
def oauth_client() -> OAuth2:
    CLIENT_ID = "CLIENT_ID"
    CLIENT_SECRET = "CLIENT_SECRET"
    AUTHORIZE_ENDPOINT = "https://www.camelot.bt/authorize"
    ACCESS_TOKEN_ENDPOINT = "https://www.camelot.bt/access-token"

    return OAuth2(
        CLIENT_ID,
        CLIENT_SECRET,
        AUTHORIZE_ENDPOINT,
        ACCESS_TOKEN_ENDPOINT,
        name="service1",
    )
