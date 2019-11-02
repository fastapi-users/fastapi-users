import jwt
from fastapi import Depends
from starlette.responses import Response

from fastapi_users.authentication.base import BaseAuthentication
from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt


class JWTAuthentication(BaseAuthentication):
    """
    Authentication using a JWT.

    :param secret: Secret used to encode the JWT.
    :param lifetime_seconds: Lifetime duration of the JWT in seconds.
    """

    token_audience: str = "fastapi-users:auth"
    secret: str
    lifetime_seconds: int

    def __init__(self, secret: str, lifetime_seconds: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds

    async def get_login_response(self, user: BaseUserDB, response: Response):
        data = {"user_id": user.id, "aud": self.token_audience}
        token = generate_jwt(data, self.lifetime_seconds, self.secret, JWT_ALGORITHM)

        return {"token": token}

    def get_current_user(self, user_db: BaseUserDatabase):
        async def _get_current_user(token: str = Depends(self.scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_user_base(user)

        return _get_current_user

    def get_current_active_user(self, user_db: BaseUserDatabase):
        async def _get_current_active_user(token: str = Depends(self.scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_active_user_base(user)

        return _get_current_active_user

    def get_current_superuser(self, user_db: BaseUserDatabase):
        async def _get_current_superuser(token: str = Depends(self.scheme)):
            user = await self._get_authentication_method(user_db)(token)
            return self._get_current_superuser_base(user)

        return _get_current_superuser

    def _get_authentication_method(self, user_db: BaseUserDatabase):
        async def authentication_method(token: str = Depends(self.scheme)):
            try:
                data = jwt.decode(
                    token,
                    self.secret,
                    audience=self.token_audience,
                    algorithms=[JWT_ALGORITHM],
                )
                user_id = data.get("user_id")
                if user_id is None:
                    return None
            except jwt.PyJWTError:
                return None
            return await user_db.get(user_id)

        return authentication_method
