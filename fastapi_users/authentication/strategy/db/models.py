from datetime import datetime, timezone
from typing import TypeVar

from pydantic import UUID4, BaseModel, Field


def now_utc():
    return datetime.now(timezone.utc)


class BaseAccessToken(BaseModel):
    """Base access token model."""

    token: str
    user_id: UUID4
    created_at: datetime = Field(default_factory=now_utc)

    class Config:
        orm_mode = True


A = TypeVar("A", bound=BaseAccessToken)
