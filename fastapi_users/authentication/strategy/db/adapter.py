import sys
from datetime import datetime
from typing import Generic, Optional, Type

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol  # pragma: no cover

from fastapi_users.authentication.strategy.db.models import A


class AccessTokenDatabase(Protocol, Generic[A]):
    """
    Protocol for retrieving, creating and updating access tokens from a database.

    :param access_token_model: Pydantic model of an access token.
    """

    access_token_model: Type[A]

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[A]:
        """Get a single access token by token."""
        ...  # pragma: no cover

    async def create(self, access_token: A) -> A:
        """Create an access token."""
        ...  # pragma: no cover

    async def update(self, access_token: A) -> A:
        """Update an access token."""
        ...  # pragma: no cover

    async def delete(self, access_token: A) -> None:
        """Delete an access token."""
        ...  # pragma: no cover
