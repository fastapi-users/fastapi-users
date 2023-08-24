import uuid
import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Type

from filuta_fastapi_users.authentication.strategy.db import AP, AccessTokenDatabase
from filuta_fastapi_users.models import ID
from sqlalchemy import ForeignKey, String, select, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from .generics import GUID, TIMESTAMPAware, now_utc


class SQLAlchemyBaseAccessTokenTable(Generic[ID]):
    """Base SQLAlchemy access token table definition."""

    __tablename__ = "access_tokens"

    if TYPE_CHECKING:  # pragma: no cover
        token: str
        created_at: datetime
        scopes: str
        mfa_scopes: json
        user_id: ID
    else:
        token: Mapped[str] = mapped_column(String(length=43), primary_key=True)
        scopes: Mapped[str] = mapped_column(String(length=255))
        mfa_scopes: Mapped[json] = mapped_column(JSON())
        created_at: Mapped[datetime] = mapped_column(
            TIMESTAMPAware(timezone=True), index=True, nullable=False, default=now_utc
        )


class SQLAlchemyBaseAccessTokenTableUUID(SQLAlchemyBaseAccessTokenTable[uuid.UUID]):
    if TYPE_CHECKING:  # pragma: no cover
        user_id: uuid.UUID
    else:

        @declared_attr
        def user_id(cls) -> Mapped[GUID]:
            return mapped_column(
                GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False
            )


class SQLAlchemyAccessTokenDatabase(Generic[AP], AccessTokenDatabase[AP]):
    """
    Access token database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param access_token_table: SQLAlchemy access token model.
    """

    def __init__(
        self,
        session: AsyncSession,
        access_token_table: Type[AP],
    ):
        self.session = session
        self.access_token_table = access_token_table

    async def get_by_token(
        self, 
        token: str, 
        max_age: Optional[datetime] = None,
        authorized: bool = False,
        ignore_expired: bool = False,
    ) -> Optional[AP]:
        
        statement = select(self.access_token_table).where(
            self.access_token_table.token == token  # type: ignore
        )
        
        if ignore_expired:
            max_age = None
        
        if max_age is not None:
            statement = statement.where(
                self.access_token_table.created_at >= max_age  # type: ignore
            )
            
        if authorized:
            statement = statement.where(
                self.access_token_table.scopes == "approved"  # type: ignore            
            )

        results = await self.session.execute(statement)
        return results.scalar_one_or_none()

    async def create(self, create_dict: Dict[str, Any]) -> AP:
        access_token = self.access_token_table(**create_dict)
        self.session.add(access_token)
        await self.session.commit()
        await self.session.refresh(access_token)
        return access_token

    async def update(self, access_token: AP, update_dict: Dict[str, Any]) -> AP:
        for key, value in update_dict.items():
            setattr(access_token, key, value)
        
        self.session.add(access_token)
        
        await self.session.commit()
        await self.session.refresh(access_token)
        return access_token

    async def delete(self, access_token: AP) -> None:
        await self.session.delete(access_token)
        await self.session.commit()
        
    async def delete_all_records_for_user(self, user):
        statement = select(self.access_token_table).where(self.access_token_table.user_id == user.id)
        results = await self.session.execute(statement)
        tokens = results.scalars().all()
        
        for token in tokens:
            await self.session.delete(token)

        await self.session.commit()