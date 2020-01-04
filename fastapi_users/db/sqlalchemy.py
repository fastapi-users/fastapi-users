from typing import List, Optional, Type

from databases import Database
from sqlalchemy import Boolean, Column, String, Table

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class SQLAlchemyBaseUserTable:
    """Base SQLAlchemy users table definition."""

    __tablename__ = "user"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)


class SQLAlchemyUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for SQLAlchemy.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param database: `Database` instance from `encode/databases`.
    :param users: SQLAlchemy users table instance.
    """

    database: Database
    users: Table

    def __init__(self, user_db_model: Type[UD], database: Database, users: Table):
        super().__init__(user_db_model)
        self.database = database
        self.users = users

    async def list(self) -> List[UD]:
        query = self.users.select()
        users = await self.database.fetch_all(query)
        return [self.user_db_model(**user) for user in users]

    async def get(self, id: str) -> Optional[UD]:
        query = self.users.select().where(self.users.c.id == id)
        user = await self.database.fetch_one(query)
        return self.user_db_model(**user) if user else None

    async def get_by_email(self, email: str) -> Optional[UD]:
        query = self.users.select().where(self.users.c.email == email)
        user = await self.database.fetch_one(query)
        return self.user_db_model(**user) if user else None

    async def create(self, user: UD) -> UD:
        query = self.users.insert().values(**user.dict())
        await self.database.execute(query)
        return user

    async def update(self, user: UD) -> UD:
        query = (
            self.users.update().where(self.users.c.id == user.id).values(**user.dict())
        )
        await self.database.execute(query)
        return user

    async def delete(self, user: UD) -> None:
        query = self.users.delete().where(self.users.c.id == user.id)
        await self.database.execute(query)
