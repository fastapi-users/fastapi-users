"""
Override dependencies works exactly with your api object

from src.main import api_v1 as app
@pytest.fixture(scope='session')
def get_test_user():
    yield TEST_USER
app.dependency_overrides[current_user] = lambda: get_test_user
"""
import typing as tp
import httpx
import asyncio
import pytest

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.app import app
from app.db import Base, get_async_session
from app.users import get_user_db, get_user_manager, UserManager

DATABASE_URL_TEST = "sqlite+aiosqlite:///./pytest.db"
TEST_USER_EMAIL = 'user@example.com'
TEST_USER_PASSWORD = "test_user$example1password"
TEST_USER = None

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_factory = async_sessionmaker(engine_test, expire_on_commit=False)
Base.metadata.bind = engine_test


async def override_get_async_session() -> tp.AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


async def add_user():
    session: AsyncSession = async_session_factory()

    # Call async generator
    user_db = await get_user_db(session=session).__anext__()
    manager: UserManager = await get_user_manager(user_db=user_db).__anext__()
    from fastapi_users.schemas import BaseUserCreate, EmailStr

    uc = BaseUserCreate(email=EmailStr(TEST_USER_EMAIL),
                        password=TEST_USER_PASSWORD,
                        is_active=True,
                        is_superuser=False,
                        is_verified=True)
    global TEST_USER
    TEST_USER = await manager.create(user_create=uc)


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await add_user()
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def jwt_authorized_async_client() -> tp.AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=app,
                                 base_url="http://0.0.0.0:8100/", follow_redirects=True) as ac:
        auth_req = await ac.post('auth/jwt/login',
                                 data={'username': TEST_USER_EMAIL,
                                       'password': TEST_USER_PASSWORD})
        assert auth_req.status_code == 200

        data = auth_req.json()
        ac.headers['Authorization'] = f'{data["token_type"]} {data["access_token"]}'
        yield ac


@pytest.fixture(scope="function")
async def async_client() -> tp.AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=app,
                                 base_url="http://0.0.0.0:8100/", follow_redirects=True) as ac:
        yield ac


@pytest.fixture(scope="function")
async def override_current_user_async_client() -> tp.AsyncGenerator[httpx.AsyncClient, None]:
    from app.users import current_active_user

    app.dependency_overrides[current_active_user] = lambda: TEST_USER

    async with httpx.AsyncClient(app=app,
                                 base_url="http://0.0.0.0:8100/", follow_redirects=True) as ac:
        yield ac
