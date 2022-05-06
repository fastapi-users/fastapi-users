import asyncio
import dataclasses
import uuid
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    Union,
)
from unittest.mock import MagicMock

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI, Response
from httpx_oauth.oauth2 import OAuth2
from pydantic import UUID4, SecretStr
from pytest_mock import MockerFixture

from fastapi_users import exceptions, models, schemas
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.db import BaseUserDatabase
from fastapi_users.jwt import SecretType
from fastapi_users.manager import BaseUserManager, UUIDIDMixin
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.password import PasswordHelper

password_helper = PasswordHelper()
guinevere_password_hash = password_helper.hash("guinevere")
angharad_password_hash = password_helper.hash("angharad")
viviane_password_hash = password_helper.hash("viviane")
lancelot_password_hash = password_helper.hash("lancelot")
excalibur_password_hash = password_helper.hash("excalibur")


IDType = uuid.UUID


@dataclasses.dataclass
class UserModel(models.UserProtocol[IDType]):
    email: str
    hashed_password: str
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    first_name: Optional[str] = None


@dataclasses.dataclass
class OAuthAccountModel(models.OAuthAccountProtocol[IDType]):
    oauth_name: str
    access_token: str
    account_id: str
    account_email: str
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None


@dataclasses.dataclass
class UserOAuthModel(UserModel):
    oauth_accounts: List[OAuthAccountModel] = dataclasses.field(default_factory=list)


class User(schemas.BaseUser[IDType]):
    first_name: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    first_name: Optional[str]


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str]


class UserOAuth(User, schemas.BaseOAuthAccountMixin):
    pass


class BaseTestUserManager(
    Generic[models.UP], UUIDIDMixin, BaseUserManager[models.UP, IDType]
):
    reset_password_token_secret = "SECRET"
    verification_token_secret = "SECRET"

    async def validate_password(
        self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:
        if len(password) < 3:
            raise exceptions.InvalidPasswordException(
                reason="Password should be at least 3 characters"
            )


class UserManager(BaseTestUserManager[UserModel]):
    pass


class UserManagerOAuth(BaseTestUserManager[UserOAuthModel]):
    pass


class UserManagerMock(BaseTestUserManager[models.UP]):
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
def user() -> UserModel:
    return UserModel(
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
    )


@pytest.fixture
def user_oauth(
    oauth_account1: OAuthAccountModel, oauth_account2: OAuthAccountModel
) -> UserOAuthModel:
    return UserOAuthModel(
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
        oauth_accounts=[oauth_account1, oauth_account2],
    )


@pytest.fixture
def inactive_user() -> UserModel:
    return UserModel(
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
    )


@pytest.fixture
def inactive_user_oauth(oauth_account3: OAuthAccountModel) -> UserOAuthModel:
    return UserOAuthModel(
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
        oauth_accounts=[oauth_account3],
    )


@pytest.fixture
def verified_user() -> UserModel:
    return UserModel(
        email="lake.lady@camelot.bt",
        hashed_password=excalibur_password_hash,
        is_active=True,
        is_verified=True,
    )


@pytest.fixture
def verified_user_oauth(oauth_account4: OAuthAccountModel) -> UserOAuthModel:
    return UserOAuthModel(
        email="lake.lady@camelot.bt",
        hashed_password=excalibur_password_hash,
        is_active=False,
        oauth_accounts=[oauth_account4],
    )


@pytest.fixture
def superuser() -> UserModel:
    return UserModel(
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
    )


@pytest.fixture
def superuser_oauth() -> UserOAuthModel:
    return UserOAuthModel(
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        oauth_accounts=[],
    )


@pytest.fixture
def verified_superuser() -> UserModel:
    return UserModel(
        email="the.real.merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        is_verified=True,
    )


@pytest.fixture
def verified_superuser_oauth() -> UserOAuthModel:
    return UserOAuthModel(
        email="the.real.merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        is_verified=True,
        oauth_accounts=[],
    )


@pytest.fixture
def oauth_account1() -> OAuthAccountModel:
    return OAuthAccountModel(
        oauth_name="service1",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth1",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account2() -> OAuthAccountModel:
    return OAuthAccountModel(
        oauth_name="service2",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth2",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account3() -> OAuthAccountModel:
    return OAuthAccountModel(
        oauth_name="service3",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="inactive_user_oauth1",
        account_email="percival@camelot.bt",
    )


@pytest.fixture
def oauth_account4() -> OAuthAccountModel:
    return OAuthAccountModel(
        oauth_name="service4",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="verified_user_oauth1",
        account_email="lake.lady@camelot.bt",
    )


@pytest.fixture
def oauth_account5() -> OAuthAccountModel:
    return OAuthAccountModel(
        oauth_name="service5",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="verified_superuser_oauth1",
        account_email="the.real.merlin@camelot.bt",
    )


@pytest.fixture
def mock_user_db(
    user: UserModel,
    verified_user: UserModel,
    inactive_user: UserModel,
    superuser: UserModel,
    verified_superuser: UserModel,
) -> BaseUserDatabase[UserModel, IDType]:
    class MockUserDatabase(BaseUserDatabase[UserModel, IDType]):
        async def get(self, id: UUID4) -> Optional[UserModel]:
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

        async def get_by_email(self, email: str) -> Optional[UserModel]:
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

        async def create(self, create_dict: Dict[str, Any]) -> UserModel:
            return UserModel(**create_dict)

        async def update(
            self, user: UserModel, update_dict: Dict[str, Any]
        ) -> UserModel:
            for field, value in update_dict.items():
                setattr(user, field, value)
            return user

        async def delete(self, user: UserModel) -> None:
            pass

    return MockUserDatabase()


@pytest.fixture
def mock_user_db_oauth(
    user_oauth: UserOAuthModel,
    verified_user_oauth: UserOAuthModel,
    inactive_user_oauth: UserOAuthModel,
    superuser_oauth: UserOAuthModel,
    verified_superuser_oauth: UserOAuthModel,
) -> BaseUserDatabase[UserOAuthModel, IDType]:
    class MockUserDatabase(BaseUserDatabase[UserOAuthModel, IDType]):
        async def get(self, id: UUID4) -> Optional[UserOAuthModel]:
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

        async def get_by_email(self, email: str) -> Optional[UserOAuthModel]:
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
        ) -> Optional[UserOAuthModel]:
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

        async def create(self, create_dict: Dict[str, Any]) -> UserOAuthModel:
            return UserOAuthModel(**create_dict)

        async def update(
            self, user: UserOAuthModel, update_dict: Dict[str, Any]
        ) -> UserOAuthModel:
            for field, value in update_dict.items():
                setattr(user, field, value)
            return user

        async def delete(self, user: UserOAuthModel) -> None:
            pass

        async def add_oauth_account(
            self, user: UserOAuthModel, create_dict: Dict[str, Any]
        ) -> UserOAuthModel:
            oauth_account = OAuthAccountModel(**create_dict)
            user.oauth_accounts.append(oauth_account)
            return user

        async def update_oauth_account(  # type: ignore
            self,
            user: UserOAuthModel,
            oauth_account: OAuthAccountModel,
            update_dict: Dict[str, Any],
        ) -> UserOAuthModel:
            for field, value in update_dict.items():
                setattr(oauth_account, field, value)
            updated_oauth_accounts = []
            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_id == oauth_account.account_id
                    and existing_oauth_account.oauth_name == oauth_account.oauth_name
                ):
                    updated_oauth_accounts.append(oauth_account)
                else:
                    updated_oauth_accounts.append(existing_oauth_account)
            return user

    return MockUserDatabase()


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


class MockStrategy(Strategy[UserModel, IDType]):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[UserModel, IDType]
    ) -> Optional[UserModel]:
        if token is not None:
            try:
                parsed_id = user_manager.parse_id(token)
                return await user_manager.get(parsed_id)
            except (exceptions.InvalidID, exceptions.UserNotExists):
                return None
        return None

    async def write_token(self, user: UserModel) -> str:
        return str(user.id)

    async def destroy_token(self, token: str, user: UserModel) -> None:
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
