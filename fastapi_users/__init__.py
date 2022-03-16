"""Ready-to-use and customizable users management for FastAPI."""

__version__ = "9.2.6"

from fastapi_users import models  # noqa: F401
from fastapi_users.fastapi_users import FastAPIUsers  # noqa: F401
from fastapi_users.manager import (  # noqa: F401
    BaseUserManager,
    InvalidPasswordException,
)

__all__ = [
    "models",
    "FastAPIUsers",
    "BaseUserManager",
    "InvalidPasswordException",
]
