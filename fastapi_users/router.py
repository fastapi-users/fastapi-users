from fastapi import APIRouter, HTTPException
from starlette import status

from fastapi_users.db import UserDBInterface
from fastapi_users.models import UserCreate, UserDB, UserLogin
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

        @router.post('/login')
        async def login(user_login: UserLogin):
            user = await userDB.authenticate(user_login)

            if user is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            elif not user.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            return user

        return router
