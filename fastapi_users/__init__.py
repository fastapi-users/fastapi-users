"""Ready-to-use and customizable users management for FastAPI."""

__version__ = "7.0.0"

from fastapi_users import models  # noqa: F401
from fastapi_users.fastapi_users import FastAPIUsers  # noqa: F401
from fastapi_users.user import InvalidPasswordException  # noqa: F401
