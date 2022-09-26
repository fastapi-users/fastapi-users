from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Generic, Iterable, Optional, Set

from pydantic import BaseModel, Field, validator

from fastapi_users import models
from fastapi_users.manager import BaseUserManager
from fastapi_users.scopes import Scope, SystemScope


class TokenData(BaseModel):
    user_id: Any
    created_at: datetime
    expires_at: Optional[datetime]
    last_authenticated: datetime
    scopes: Set[Scope]

    @validator("scopes")
    def _validate_scopes(cls, v: Set[Scope]) -> Set[Scope]:
        def _validate_scope(scope: Scope) -> Scope:
            if isinstance(scope, SystemScope):
                return scope
            # As we are going to use these for OAuth 2.0 tokens,
            # all scopes should be valid OAuth 2.0 scopes - see
            # https://www.rfc-editor.org/rfc/rfc6749#section-3.3
            assert re.match(r"^[!#-\[\]-~]+$", scope)
            try:
                return SystemScope(scope)
            except ValueError:
                return scope

        return set(_validate_scope(x) for x in v)

    @property
    def scope(self) -> str:
        return " ".join(str(x) for x in self.scopes)

    @property
    def fresh(self) -> bool:
        return self.created_at == self.last_authenticated

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False
        return self.expires_at <= datetime.now(timezone.utc)

    @property
    def time_to_expiry(self) -> Optional[timedelta]:
        if self.expires_at is None:
            return None
        return self.expires_at - datetime.now(timezone.utc)

    async def lookup_user(
        self, user_manager: BaseUserManager[models.UP, models.ID]
    ) -> UserTokenData[models.UP, models.ID]:
        user_id = user_manager.parse_id(self.user_id)
        return UserTokenData(
            user_id=user_id,
            **self.dict(exclude={"user_id"}),
            user=await user_manager.get(user_id),
        )


class UserTokenData(TokenData, Generic[models.UP, models.ID]):
    user: models.UP = Field(..., exclude=True)

    @classmethod
    def issue_now(
        cls,
        user: models.UserProtocol[models.ID],
        lifetime_seconds: Optional[int] = None,
        last_authenticated: Optional[datetime] = None,
        scopes: Optional[Iterable[Scope]] = None,
    ) -> UserTokenData[models.UP, models.ID]:

        scopes = scopes or set()

        now = datetime.now(timezone.utc)

        if lifetime_seconds is None:
            expires_at = None
        else:
            expires_at = now + timedelta(seconds=lifetime_seconds)

        return cls(
            user_id=user.id,
            created_at=now,
            expires_at=expires_at,
            last_authenticated=last_authenticated or now,
            scopes=set(scopes),
            user=user,
        )

    class Config:
        arbitrary_types_allowed = True
