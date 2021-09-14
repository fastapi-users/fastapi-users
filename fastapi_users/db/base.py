from typing import Callable, Generic, Optional, Type

from pydantic import UUID4

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


UserDatabaseDependency = Callable[..., BaseUserDatabase[UD]]
