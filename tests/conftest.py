import asyncio
from typing import AsyncGenerator, List, Optional

import asynctest
import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import Depends, FastAPI, Response
from fastapi.security import OAuth2PasswordBearer
from httpx_oauth.oauth2 import OAuth2
from pydantic import UUID4
from starlette.applications import ASGIApp

from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseOAuthAccount, BaseOAuthAccountMixin, BaseUserDB
from fastapi_users.password import get_password_hash
from fastapi_users.user import InvalidPasswordException, ValidatePasswordProtocol

guinevere_password_hash = get_password_hash("guinevere")
angharad_password_hash = get_password_hash("angharad")
viviane_password_hash = get_password_hash("viviane")
lancelot_password_hash = get_password_hash("lancelot")
excalibur_password_hash = get_password_hash("excalibur")


class User(models.BaseUser):
    first_name: Optional[str]


class UserCreate(models.BaseUserCreate):
    first_name: Optional[str]


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


class UserOAuth(User, BaseOAuthAccountMixin):
    pass


class UserDBOAuth(UserOAuth, UserDB):
    pass


@pytest.fixture(scope="session")
def event_loop():
    """Force the pytest-asyncio loop to be the main one."""
    loop = asyncio.get_event_loop()
    yield loop


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
        username="percival"
    )


@pytest.fixture
def verified_user() -> UserDB:
    return UserDB(
        email="lake.lady@camelot.bt",
        hashed_password=excalibur_password_hash,
        is_active=True,
        is_verified=True,
        username="lake"
    )


@pytest.fixture
def verified_user_oauth(oauth_account4) -> UserDBOAuth:
    return UserDBOAuth(
        email="lake.lady@camelot.bt",
        hashed_password=excalibur_password_hash,
        is_active=False,
        oauth_accounts=[oauth_account4],
        username="lake"
    )


@pytest.fixture
def superuser() -> UserDB:
    return UserDB(
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        username="merlin"
    )


@pytest.fixture
def superuser_oauth() -> UserDBOAuth:
    return UserDBOAuth(
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        oauth_accounts=[],
        username="merlin"
    )


@pytest.fixture
def verified_superuser() -> UserDB:
    return UserDB(
        email="the.real.merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        is_verified=True,
        username="merlin_real"
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


class MockAuthentication(BaseAuthentication[str]):
    def __init__(self, name: str = "mock"):
        super().__init__(name, logout=True)
        self.scheme = OAuth2PasswordBearer("/login", auto_error=False)

    async def __call__(self, credentials: Optional[str], user_db: BaseUserDatabase):
        if credentials is not None:
            try:
                token_uuid = UUID4(credentials)
                return await user_db.get(token_uuid)
            except ValueError:
                return None
        return None

    async def get_login_response(self, user: BaseUserDB, response: Response):
        return {"token": user.id}

    async def get_logout_response(self, user: BaseUserDB, response: Response):
        return None


@pytest.fixture
def mock_authentication():
    return MockAuthentication()


@pytest.fixture
def get_test_client():
    async def _get_test_client(app: ASGIApp) -> AsyncGenerator[httpx.AsyncClient, None]:
        async with LifespanManager(app):
            async with httpx.AsyncClient(
                app=app, base_url="http://app.io"
            ) as test_client:
                yield test_client

    return _get_test_client


@pytest.fixture
@pytest.mark.asyncio
def get_test_auth_client(mock_user_db, get_test_client):
    async def _get_test_auth_client(
        backends: List[BaseAuthentication],
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        app = FastAPI()
        authenticator = Authenticator(backends, mock_user_db)

        @app.get("/test-current-user")
        def test_current_user(user: UserDB = Depends(authenticator.current_user())):
            return user

        @app.get("/test-current-active-user")
        def test_current_active_user(
            user: UserDB = Depends(authenticator.current_user(active=True)),
        ):
            return user

        @app.get("/test-current-superuser")
        def test_current_superuser(
            user: UserDB = Depends(
                authenticator.current_user(active=True, superuser=True)
            ),
        ):
            return user

        async for client in get_test_client(app):
            yield client

    return _get_test_auth_client


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


@pytest.fixture
def validate_password() -> ValidatePasswordProtocol:
    async def _validate_password(password: str, user: models.UD) -> None:
        if len(password) < 3:
            raise InvalidPasswordException(
                reason="Password should be at least 3 characters"
            )

    return asynctest.CoroutineMock(wraps=_validate_password)
