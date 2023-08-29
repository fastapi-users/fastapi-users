from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import UUID4
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Dialect
from sqlalchemy.types import CHAR, TIMESTAMP, TypeDecorator, TypeEngine


class GUID(TypeDecorator[UUID]):  # pragma: no cover
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(36), storing as regular strings.
    """

    class UUIDChar(CHAR):
        python_type = UUID4

    impl = UUIDChar
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[UUID] | TypeEngine[str]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Any, dialect: Dialect) -> str | None:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        elif not isinstance(value, UUID):
            return str(UUID(value))
        else:
            return str(value)

    def process_result_value(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return value
        else:
            if not isinstance(value, UUID):
                value = UUID(value)
            return value


def now_utc() -> datetime:
    return datetime.now(UTC)


class TIMESTAMPAware(TypeDecorator[datetime]):  # pragma: no cover
    """
    MySQL and SQLite will always return naive-Python datetimes.

    We store everything as UTC, but we want to have
    only offset-aware Python datetimes, even with MySQL and SQLite.
    """

    impl = TIMESTAMP
    cache_ok = True

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is not None and dialect.name != "postgresql":
            return value.replace(tzinfo=UTC)
        return value
