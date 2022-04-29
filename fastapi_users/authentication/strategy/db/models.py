import sys
import uuid
from datetime import datetime
from typing import TypeVar

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol  # pragma: no cover


class AccessTokenProtocol(Protocol):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: uuid.UUID
    created_at: datetime

    def __init__(self, *args, **kwargs) -> None:
        ...  # pragma: no cover


AP = TypeVar("AP", bound=AccessTokenProtocol)
