"""FastAPI Users database adapter for SQLAlchemy."""
import uuid
from typing import TYPE_CHECKING, Any, Generic

from sqlalchemy import Boolean, ForeignKey, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.sql import Select

from filuta_fastapi_users import models
from filuta_fastapi_users.db.base import BaseUserDatabase

from .generics import GUID

__version__ = "6.0.1"

UUID_ID = uuid.UUID


class SQLAlchemyBaseUserTable(Generic[models.ID]):
    """Base SQLAlchemy users table definition."""

    __tablename__ = "user"

    if TYPE_CHECKING:  # pragma: no cover
        id: models.ID
        email: str
        hashed_password: str
        is_active: bool
        is_superuser: bool
        is_poweruser: bool
        is_verified: bool
    else:
        email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
        hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
        is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
        is_poweruser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
        is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SQLAlchemyBaseUserTableUUID(SQLAlchemyBaseUserTable[UUID_ID]):
    if TYPE_CHECKING:  # pragma: no cover
        id: UUID_ID
    else:
        id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)


class SQLAlchemyBaseOAuthAccountTable(Generic[models.ID]):
    """Base SQLAlchemy OAuth account table definition."""

    __tablename__ = "oauth_account"

    if TYPE_CHECKING:  # pragma: no cover
        id: models.ID
        oauth_name: str
        access_token: str
        expires_at: int | None
        refresh_token: str | None
        account_id: str
        account_email: str
    else:
        oauth_name: Mapped[str] = mapped_column(String(length=100), index=True, nullable=False)
        access_token: Mapped[str] = mapped_column(String(length=1024), nullable=False)
        expires_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
        refresh_token: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)
        account_id: Mapped[str] = mapped_column(String(length=320), index=True, nullable=False)
        account_email: Mapped[str] = mapped_column(String(length=320), nullable=False)


class SQLAlchemyBaseOAuthAccountTableUUID(SQLAlchemyBaseOAuthAccountTable[UUID_ID]):
    if TYPE_CHECKING:  # pragma: no cover
        id: UUID_ID
        user_id: UUID_ID
    else:
        id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)

        @declared_attr
        def user_id(cls) -> Mapped[GUID]:
            return mapped_column(GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False)


class SQLAlchemyUserDatabase(Generic[models.UOAP, models.ID], BaseUserDatabase[models.UOAP, models.ID]):
    """
    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    :param oauth_account_table: Optional SQLAlchemy OAuth accounts model.
    """

    session: AsyncSession
    user_table: type[models.UOAP]
    oauth_account_table: type[SQLAlchemyBaseOAuthAccountTable[uuid.UUID]] | None

    def __init__(
        self,
        session: AsyncSession,
        user_table: type[models.UOAP],
        oauth_account_table: type[SQLAlchemyBaseOAuthAccountTable[uuid.UUID]] | None = None,
    ):
        self.session = session
        self.user_table = user_table
        self.oauth_account_table = oauth_account_table

    async def get(self, id: models.ID) -> models.UOAP | None:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> models.UOAP | None:
        statement = select(self.user_table).where(func.lower(self.user_table.email) == func.lower(email))
        return await self._get_user(statement)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> models.UOAP | None:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        statement = (
            select(self.user_table)
            .join(self.oauth_account_table)
            .where(self.oauth_account_table.oauth_name == oauth)
            .where(self.oauth_account_table.account_id == account_id)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: dict[str, Any]) -> models.UOAP:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: models.UOAP, update_dict: dict[str, Any]) -> models.UOAP:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: models.UOAP) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def add_oauth_account(self, user: models.UOAP, create_dict: dict[str, Any]) -> models.UOAP:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        await self.session.refresh(user)
        oauth_account = self.oauth_account_table(**create_dict)
        self.session.add(oauth_account)
        user.oauth_accounts.append(oauth_account)
        self.session.add(user)

        await self.session.commit()

        return user

    async def update_oauth_account(
        self, user: models.UOAP, oauth_account: models.OAP, update_dict: dict[str, Any]
    ) -> models.UOAP:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        for key, value in update_dict.items():
            setattr(oauth_account, key, value)
        self.session.add(oauth_account)
        await self.session.commit()

        return user

    async def _get_user(self, statement: Select[Any]) -> models.UOAP | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
