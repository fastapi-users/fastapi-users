import asyncio
from typing import Any, List, Mapping, Optional, Tuple

import http.cookies
import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from httpx_oauth.oauth2 import OAuth2
from starlette.applications import ASGIApp
from starlette.requests import Request
from starlette.responses import Response

from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseOAuthAccount, BaseOAuthAccountMixin, BaseUserDB
from fastapi_users.password import get_password_hash

guinevere_password_hash = get_password_hash("guinevere")
angharad_password_hash = get_password_hash("angharad")
viviane_password_hash = get_password_hash("viviane")
lancelot_password_hash = get_password_hash("lancelot")


class User(models.BaseUser):
    first_name: Optional[str]


class UserCreate(User, models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


class UserOAuth(User, BaseOAuthAccountMixin):
    pass


class UserDBOAuth(UserOAuth, UserDB):
    pass


@pytest.fixture
def event_loop():
    """Force the pytest-asyncio loop to be the main one."""
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture
def user() -> UserDB:
    return UserDB(
        id="aaa",
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
    )


@pytest.fixture
def user_oauth(oauth_account1, oauth_account2) -> UserDBOAuth:
    return UserDBOAuth(
        id="aaa",
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
        oauth_accounts=[oauth_account1, oauth_account2],
    )


@pytest.fixture
def inactive_user() -> UserDB:
    return UserDB(
        id="bbb",
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
    )


@pytest.fixture
def inactive_user_oauth(oauth_account3) -> UserDBOAuth:
    return UserDBOAuth(
        id="bbb",
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
        oauth_accounts=[oauth_account3],
    )


@pytest.fixture
def superuser() -> UserDB:
    return UserDB(
        id="ccc",
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
    )


@pytest.fixture
def superuser_oauth() -> UserDBOAuth:
    return UserDBOAuth(
        id="ccc",
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        oauth_accounts=[],
    )


@pytest.fixture
def oauth_account1() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        id="aaa",
        oauth_name="service1",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth1",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account2() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        id="bbb",
        oauth_name="service2",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth2",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account3() -> BaseOAuthAccount:
    return BaseOAuthAccount(
        id="ccc",
        oauth_name="service3",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="inactive_user_oauth1",
        account_email="percival@camelot.bt",
    )


@pytest.fixture
def mock_user_db(user, inactive_user, superuser) -> BaseUserDatabase:
    class MockUserDatabase(BaseUserDatabase[UserDB]):
        async def list(self) -> List[UserDB]:
            return [user, inactive_user, superuser]

        async def get(self, id: str) -> Optional[UserDB]:
            if id == user.id:
                return user
            if id == inactive_user.id:
                return inactive_user
            if id == superuser.id:
                return superuser
            return None

        async def get_by_email(self, email: str) -> Optional[UserDB]:
            if email == user.email:
                return user
            if email == inactive_user.email:
                return inactive_user
            if email == superuser.email:
                return superuser
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
    user_oauth, inactive_user_oauth, superuser_oauth
) -> BaseUserDatabase:
    class MockUserDatabase(BaseUserDatabase[UserDBOAuth]):
        async def list(self) -> List[UserDBOAuth]:
            return [user_oauth, inactive_user_oauth, superuser_oauth]

        async def get(self, id: str) -> Optional[UserDBOAuth]:
            if id == user_oauth.id:
                return user_oauth
            if id == inactive_user_oauth.id:
                return inactive_user_oauth
            if id == superuser_oauth.id:
                return superuser_oauth
            return None

        async def get_by_email(self, email: str) -> Optional[UserDBOAuth]:
            if email == user_oauth.email:
                return user_oauth
            if email == inactive_user_oauth.email:
                return inactive_user_oauth
            if email == superuser_oauth.email:
                return superuser_oauth
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


class MockAuthentication(BaseAuthentication):
    def __init__(self, name: str = "mock"):
        super().__init__(name)
        self.scheme = OAuth2PasswordBearer("/users/login", auto_error=False)

    async def __call__(self, request: Request, user_db: BaseUserDatabase):
        token = await self.scheme.__call__(request)
        if token is not None:
            return await user_db.get(token)
        return None

    async def get_login_response(self, user: BaseUserDB, response: Response):
        return {"token": user.id}


@pytest.fixture
def mock_authentication():
    return MockAuthentication()


@pytest.fixture
def request_builder():
    def _request_builder(
        headers: Mapping[str, Any] = None, cookies: Mapping[str, str] = None
    ) -> Request:
        encoded_headers: List[Tuple[bytes, bytes]] = []

        if headers is not None:
            encoded_headers += [
                (key.lower().encode("latin-1"), headers[key].encode("latin-1"))
                for key in headers
            ]

        if cookies is not None:
            for key in cookies:
                cookie = http.cookies.SimpleCookie()  # type: http.cookies.BaseCookie
                cookie[key] = cookies[key]
                cookie_val = cookie.output(header="").strip()
                encoded_headers.append((b"cookie", cookie_val.encode("latin-1")))

        scope = {
            "type": "http",
            "headers": encoded_headers,
        }
        return Request(scope)

    return _request_builder


@pytest.fixture
def get_test_client():
    async def _get_test_client(app: ASGIApp) -> httpx.AsyncClient:
        async with LifespanManager(app):
            async with httpx.AsyncClient(
                app=app, base_url="http://app.io"
            ) as test_client:
                return test_client

    return _get_test_client


@pytest.fixture
@pytest.mark.asyncio
def get_test_auth_client(mock_user_db, get_test_client):
    async def _get_test_auth_client(
        backends: List[BaseAuthentication],
    ) -> httpx.AsyncClient:
        app = FastAPI()
        authenticator = Authenticator(backends, mock_user_db)

        @app.get("/test-current-user")
        def test_current_user(user: UserDB = Depends(authenticator.get_current_user),):
            return user

        @app.get("/test-current-active-user")
        def test_current_active_user(
            user: UserDB = Depends(authenticator.get_current_active_user),
        ):
            return user

        @app.get("/test-current-superuser")
        def test_current_superuser(
            user: UserDB = Depends(authenticator.get_current_superuser),
        ):
            return user

        return await get_test_client(app)

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
