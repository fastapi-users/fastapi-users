from typing import List

from fastapi_users.models import UserDB


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
