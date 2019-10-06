from typing import List

from fastapi_users.models import UserDB, UserLogin
from fastapi_users.password import get_password_hash, verify_password


class UserDBInterface:
    """
    Common interface exposing methods to list, get, create and update users in
    the database.
    """

    async def list(self) -> List[UserDB]:
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> UserDB:
        raise NotImplementedError()

    async def create(self, user: UserDB) -> UserDB:
        raise NotImplementedError()

    async def authenticate(self, user_login) -> UserLogin:
        user = await self.get_by_email(user_login.email)

        # Always run the hasher to mitigate timing attack
        # Inspired from Django: https://code.djangoproject.com/ticket/20760
        get_password_hash(user_login.password)

        if user is None or not verify_password(user_login.password, user.hashed_password):
            return None

        return user
