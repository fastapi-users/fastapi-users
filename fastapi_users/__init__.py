"""Ready-to-use and customizable users management for FastAPI."""

__version__ = "10.0.0"

from fastapi_users import models, schemas  # noqa: F401
from fastapi_users.fastapi_users import FastAPIUsers  # noqa: F401
from fastapi_users.manager import (  # noqa: F401
    BaseUserManager,
    IntegerIDMixin,
    InvalidID,
    InvalidPasswordException,
    UUIDIDMixin,
)

__all__ = [
    "schemas",
    "FastAPIUsers",
    "BaseUserManager",
    "InvalidPasswordException",
    "InvalidID",
    "UUIDIDMixin",
    "IntegerIDMixin",
]
