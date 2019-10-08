from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import User, UserCreate, UserDB
from fastapi_users.password import get_password_hash


class UserRouter:

    def __new__(cls, userDB: BaseUserDatabase, auth: BaseAuthentication) -> APIRouter:
        router = APIRouter()

        @router.post('/register', response_model=User)
        async def register(user: UserCreate):
            hashed_password = get_password_hash(user.password)
            db_user = UserDB(**user.dict(), hashed_password=hashed_password)
            created_user = await userDB.create(db_user)
            return created_user

        @router.post('/login')
        async def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends()):
            user = await userDB.authenticate(credentials)

            if user is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            elif not user.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            return await auth.get_login_response(user, response)

        return router
