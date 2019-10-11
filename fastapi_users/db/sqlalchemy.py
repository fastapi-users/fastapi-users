from typing import List, cast

from databases import Database
from sqlalchemy import Boolean, Column, String, Table

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class SQLAlchemyBaseUserTable:
    """Base SQLAlchemy users table definition."""

    __tablename__ = "user"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)


class SQLAlchemyUserDatabase(BaseUserDatabase):
    """
    Database adapter for SQLAlchemy.

    :param database: `Database` instance from `encode/databases`.
    :param users: SQLAlchemy users table instance.
    """

    database: Database
    users: Table

    def __init__(self, database: Database, users: Table):
        self.database = database
        self.users = users

    async def list(self) -> List[BaseUserDB]:
        query = self.users.select()
        return cast(List[BaseUserDB], await self.database.fetch_all(query))

    async def get(self, id: str) -> BaseUserDB:
        query = self.users.select().where(self.users.c.id == id)
        return cast(BaseUserDB, await self.database.fetch_one(query))

    async def get_by_email(self, email: str) -> BaseUserDB:
        query = self.users.select().where(self.users.c.email == email)
        return cast(BaseUserDB, await self.database.fetch_one(query))

    async def create(self, user: BaseUserDB) -> BaseUserDB:
        query = self.users.insert().values(**user.dict())
        await self.database.execute(query)
        return user

    async def update(self, user: BaseUserDB) -> BaseUserDB:
        query = (
            self.users.update().where(self.users.c.id == user.id).values(**user.dict())
        )
        await self.database.execute(query)
        return user
