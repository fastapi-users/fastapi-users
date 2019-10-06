from typing import List

from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users.models import UserDB
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

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> UserDB:
        user = await self.get_by_email(credentials.username)

        # Always run the hasher to mitigate timing attack
        # Inspired from Django: https://code.djangoproject.com/ticket/20760
        get_password_hash(credentials.password)

        if user is None or not verify_password(credentials.password, user.hashed_password):
            return None

        return user
