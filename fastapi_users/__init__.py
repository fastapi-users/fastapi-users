"""Ready-to-use and customizable users management for FastAPI."""

__version__ = "9.1.1"

from fastapi_users import models  # noqa: F401
from fastapi_users.fastapi_users import FastAPIUsers  # noqa: F401
from fastapi_users.manager import (  # noqa: F401
    BaseUserManager,
    InvalidPasswordException,
)
