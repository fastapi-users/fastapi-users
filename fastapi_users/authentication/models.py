from typing import Tuple, TypeVar

TokenIdentityType = TypeVar("TokenIdentityType", contravariant=True)
TokenType = TypeVar("TokenType", covariant=True)

AccessRefreshToken = Tuple[str, str]  # First is access second is refresh
