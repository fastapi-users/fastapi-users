from fastapi_users.authentication.strategy.base import (
    BaseStrategy,
    Strategy,
    StrategyDestroyNotSupportedError,
    StrategyRefresh,
)
from fastapi_users.authentication.strategy.db import (
    AP,
    APE,
    AccessRefreshTokenDatabase,
    AccessRefreshTokenProtocol,
    AccessTokenDatabase,
    AccessTokenProtocol,
    DatabaseStrategy,
)
from fastapi_users.authentication.strategy.jwt import JWTStrategy

try:
    from fastapi_users.authentication.strategy.redis import RedisStrategy
except ImportError:  # pragma: no cover
    pass

__all__ = [
    "AP",
    "APE",
    "AccessRefreshTokenDatabase",
    "AccessRefreshTokenProtocol",
    "AccessTokenDatabase",
    "AccessTokenProtocol",
    "BaseStrategy",
    "DatabaseStrategy",
    "JWTStrategy",
    "Strategy",
    "StrategyDestroyNotSupportedError",
    "StrategyRefresh",
    "RedisStrategy",
]
