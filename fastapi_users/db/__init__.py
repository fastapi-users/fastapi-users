from typing import List

from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users.models import UserDB
from fastapi_users.password import get_password_hash, verify_and_update_password


class BaseUserDatabase:
    """
    Common interface exposing methods to list, get, create and update users in
    the database.
    """

    async def list(self) -> List[UserDB]:
        raise NotImplementedError()

    async def get(self, id: str) -> UserDB:
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> UserDB:
        raise NotImplementedError()

    async def create(self, user: UserDB) -> UserDB:
        raise NotImplementedError()

    async def update(self, user: UserDB) -> UserDB:
        raise NotImplementedError()

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> UserDB:
        user = await self.get_by_email(credentials.username)

        # Always run the hasher to mitigate timing attack
        # Inspired from Django: https://code.djangoproject.com/ticket/20760
        get_password_hash(credentials.password)

        if user is None:
            return None
        else:
            verified, updated_password_hash = verify_and_update_password(
                credentials.password, user.hashed_password
            )
            if not verified:
                return None
            # Update password hash to a more robust one if needed
            if updated_password_hash is not None:
                user.hashed_password = updated_password_hash
                await self.update(user)

        return user
