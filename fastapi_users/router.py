from fastapi import APIRouter

from fastapi_users.db import UserDBInterface
from fastapi_users.models import UserCreate, UserDB
from fastapi_users.password import get_password_hash


class UserRouter:

    def __new__(cls, userDB: UserDBInterface) -> APIRouter:
        router = APIRouter()

        @router.post('/register')
        async def register(user: UserCreate):
            hashed_password = get_password_hash(user.password)
            db_user = UserDB(**user.dict(), hashed_password=hashed_password)
            created_user = await userDB.create(db_user)
            return created_user

        return router
