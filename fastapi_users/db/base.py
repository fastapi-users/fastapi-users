from typing import Generic, Optional, Type

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4

from fastapi_users import password
from fastapi_users.models import UD


class BaseUserDatabase(Generic[UD]):
    """
    Base adapter for retrieving, creating and updating users from a database.

    :param user_db_model: Pydantic model of a DB representation of a user.
    """

    user_db_model: Type[UD]

    def __init__(self, user_db_model: Type[UD]):
        self.user_db_model = user_db_model

    async def get(self, id: UUID4) -> Optional[UD]:
        """Get a single user by id."""
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> Optional[UD]:
        """Get a single user by email."""
        raise NotImplementedError()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        """Get a single user by OAuth account id."""
        raise NotImplementedError()

    async def create(self, user: UD) -> UD:
        """Create a user."""
        raise NotImplementedError()

    async def update(self, user: UD) -> UD:
        """Update a user."""
        raise NotImplementedError()

    async def delete(self, user: UD) -> None:
        """Delete a user."""
        raise NotImplementedError()

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[UD]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.
        """
        user = await self.get_by_email(credentials.username)

        if user is None:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            password.get_password_hash(credentials.password)
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
