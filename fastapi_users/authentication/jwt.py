from datetime import datetime, timedelta

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response

from fastapi_users.authentication.base import BaseAuthentication
from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def generate_jwt(data: dict, lifetime_seconds: int, secret: str, algorithm: str) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=lifetime_seconds)
    payload["exp"] = expire
    return jwt.encode(payload, secret, algorithm=algorithm).decode("utf-8")


class JWTAuthentication(BaseAuthentication):
    """
    Authentication using a JWT.

    :param secret: Secret used to encode the JWT.
    :param lifetime_seconds: Lifetime duration of the JWT in seconds.
    """

    algorithm: str = "HS256"
    secret: str
    lifetime_seconds: int

    def __init__(self, secret: str, lifetime_seconds: int):
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds

    async def get_login_response(self, user: BaseUserDB, response: Response):
        data = {"user_id": user.id}
        token = generate_jwt(data, self.lifetime_seconds, self.secret, self.algorithm)

        return {"token": token}

    def get_current_user(self, user_db: BaseUserDatabase):
        async def _get_current_user(token: str = Depends(oauth2_scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_user_base(user)

        return _get_current_user

    def get_current_active_user(self, user_db: BaseUserDatabase):
        async def _get_current_active_user(token: str = Depends(oauth2_scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_active_user_base(user)

        return _get_current_active_user

    def get_current_superuser(self, user_db: BaseUserDatabase):
        async def _get_current_superuser(token: str = Depends(oauth2_scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_superuser_base(user)

        return _get_current_superuser

    def _get_authentication_method(self, user_db: BaseUserDatabase):
        async def authentication_method(token: str = Depends(oauth2_scheme)):
            try:
                data = jwt.decode(token, self.secret, algorithms=[self.algorithm])
                user_id = data.get("user_id")
                if user_id is None:
                    return None
            except jwt.PyJWTError:
                return None
            return await user_db.get(user_id)

        return authentication_method
