import sys
from typing import Generic, List, Optional, TypeVar

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol  # pragma: no cover

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

    def __init__(self, *args, **kwargs) -> None:
        ...  # pragma: no cover


class OAuthAccountProtocol(Protocol[ID]):
    """OAuth account protocol that ORM model should follow."""

    id: ID
    oauth_name: str
    access_token: str
    expires_at: Optional[int]
    refresh_token: Optional[str]
    account_id: str
    account_email: str

    def __init__(self, *args, **kwargs) -> None:
        ...  # pragma: no cover


UP = TypeVar("UP", bound=UserProtocol)
OAP = TypeVar("OAP", bound=OAuthAccountProtocol)


class UserOAuthProtocol(UserProtocol[ID], Generic[ID, OAP]):
    """User protocol including a list of OAuth accounts."""

    oauth_accounts: List[OAP]


UOAP = TypeVar("UOAP", bound=UserOAuthProtocol)
