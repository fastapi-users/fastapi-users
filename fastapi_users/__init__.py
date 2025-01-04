"""Ready-to-use and customizable users management for FastAPI."""

__version__ = "14.0.1"

from fastapi_users import models, schemas  # noqa: F401
from fastapi_users.exceptions import InvalidID, InvalidPasswordException
from fastapi_users.fastapi_users import FastAPIUsers  # noqa: F401
from fastapi_users.manager import (  # noqa: F401
    BaseUserManager,
    IntegerIDMixin,
    UUIDIDMixin,
)

__all__ = [
    "models",
    "schemas",
    "FastAPIUsers",
    "BaseUserManager",
    "InvalidPasswordException",
    "InvalidID",
    "UUIDIDMixin",
    "IntegerIDMixin",
]
