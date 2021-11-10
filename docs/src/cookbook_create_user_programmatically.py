import contextlib

from app.db import get_user_db
from app.models import UserCreate
from app.users import get_user_manager
from fastapi_users.manager import UserAlreadyExists

get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(email: str, password: str, is_superuser: bool = False):
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.create(
                    UserCreate(
                        email=email, password=password, is_superuser=is_superuser
                    )
                )
                print(f"User created {user}")
    except UserAlreadyExists:
        print(f"User {email} already exists")
