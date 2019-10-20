from typing import List, Optional

from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users import password
from fastapi_users.models import BaseUserDB


class BaseUserDatabase:
    """Base adapter for retrieving, creating and updating users from a database."""

    async def list(self) -> List[BaseUserDB]:
        """List all users."""
        raise NotImplementedError()

    async def get(self, id: str) -> Optional[BaseUserDB]:
        """Get a single user by id."""
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
        """Get a single user by email."""
        raise NotImplementedError()

    async def create(self, user: BaseUserDB) -> BaseUserDB:
        """Create a user."""
        raise NotImplementedError()

    async def update(self, user: BaseUserDB) -> BaseUserDB:
        """Update a user."""
        raise NotImplementedError()

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[BaseUserDB]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.
        """
        user = await self.get_by_email(credentials.username)

        # Always run the hasher to mitigate timing attack
        # Inspired from Django: https://code.djangoproject.com/ticket/20760
        password.get_password_hash(credentials.password)

        if user is None:
            return None

        verified, updated_password_hash = password.verify_and_update_password(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            user.hashed_password = updated_password_hash
            await self.update(user)

        return user
