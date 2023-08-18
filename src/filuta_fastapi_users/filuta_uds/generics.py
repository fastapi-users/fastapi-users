import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import UUID4
from sqlalchemy import CHAR, TIMESTAMP, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):  # pragma: no cover
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(36), storing as regular strings.
    """

    class UUIDChar(CHAR):
        python_type = UUID4  # type: ignore

    impl = UUIDChar
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


def now_utc():
    return datetime.now(timezone.utc)


class TIMESTAMPAware(TypeDecorator):  # pragma: no cover
    """
    MySQL and SQLite will always return naive-Python datetimes.

    We store everything as UTC, but we want to have
    only offset-aware Python datetimes, even with MySQL and SQLite.
    """

    impl = TIMESTAMP
    cache_ok = True

    def process_result_value(self, value: Optional[datetime], dialect):
        if value is not None and dialect.name != "postgresql":
            return value.replace(tzinfo=timezone.utc)
        return value
