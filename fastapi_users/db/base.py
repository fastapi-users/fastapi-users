from typing import Any, Dict, Generic, Optional

from fastapi_users.models import ID, OAP, UOAP, UP
from fastapi_users.types import DependencyCallable


class BaseUserDatabase(Generic[UP, ID]):
    """Base adapter for retrieving, creating and updating users from a database."""

    async def get(self, id: ID) -> Optional[UP]:
        """Get a single user by id."""
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> Optional[UP]:
        """Get a single user by email."""
        raise NotImplementedError()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UP]:
        """Get a single user by OAuth account id."""
        raise NotImplementedError()

    async def create(self, create_dict: Dict[str, Any]) -> UP:
        """Create a user."""
        raise NotImplementedError()

    async def update(self, user: UP, update_dict: Dict[str, Any]) -> UP:
        """Update a user."""
        raise NotImplementedError()

    async def delete(self, user: UP) -> None:
        """Delete a user."""
        raise NotImplementedError()

    async def add_oauth_account(
        self: "BaseUserDatabase[UOAP, ID]", user: UOAP, create_dict: Dict[str, Any]
    ) -> UOAP:
        """Create an OAuth account and add it to the user."""
        raise NotImplementedError()

    async def update_oauth_account(
        self: "BaseUserDatabase[UOAP, ID]",
        user: UOAP,
        oauth_account: OAP,
        update_dict: Dict[str, Any],
    ) -> UOAP:
        """Update an OAuth account on a user."""
        raise NotImplementedError()


UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID]]
