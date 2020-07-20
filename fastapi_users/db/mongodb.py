from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import UUID4
from pymongo.collation import Collation

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class MongoDBUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for MongoDB.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param collection: Collection instance from `motor`.
    """

    collection: AsyncIOMotorCollection
    email_collation: Collation

    def __init__(
        self,
        user_db_model: Type[UD],
        collection: AsyncIOMotorCollection,
        email_collation: Optional[Collation] = None,
    ):
        super().__init__(user_db_model)
        self.collection = collection
        self.collection.create_index("id", unique=True)
        self.collection.create_index("email", unique=True)

        if email_collation:
            self.email_collation = email_collation  # pragma: no cover
        else:
            self.email_collation = Collation("en", strength=2)

        self.collection.create_index(
            "email",
            name="case_insensitive_email_index",
            collation=self.email_collation,
        )

    async def get(self, id: UUID4) -> Optional[UD]:
        user = await self.collection.find_one({"id": id})
        return self.user_db_model(**user) if user else None

    async def get_by_email(self, email: str) -> Optional[UD]:
        user = await self.collection.find_one(
            {"email": email}, collation=self.email_collation
        )
        return self.user_db_model(**user) if user else None

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        user = await self.collection.find_one(
            {
                "oauth_accounts.oauth_name": oauth,
                "oauth_accounts.account_id": account_id,
            }
        )
        return self.user_db_model(**user) if user else None

    async def create(self, user: UD) -> UD:
        await self.collection.insert_one(user.dict())
        return user

    async def update(self, user: UD) -> UD:
        await self.collection.replace_one({"id": user.id}, user.dict())
        return user

    async def delete(self, user: UD) -> None:
        await self.collection.delete_one({"id": user.id})
