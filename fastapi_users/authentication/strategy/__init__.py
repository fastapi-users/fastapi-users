from fastapi_users.authentication.strategy.base import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.authentication.strategy.jwt import JWTStrategy

try:
    from fastapi_users.authentication.strategy.redis import RedisStrategy
except ImportError:  # pragma: no cover
    pass

__all__ = [
    "JWTStrategy",
    "Strategy",
    "StrategyDestroyNotSupportedError",
    "RedisStrategy",
]
