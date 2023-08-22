import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional
import random
from datetime import datetime, timedelta

from filuta_fastapi_users import exceptions, models
from filuta_fastapi_users.authentication.strategy.base import Strategy
from filuta_fastapi_users.authentication.strategy.db.adapter import RefreshTokenDatabase
from filuta_fastapi_users.authentication.strategy.db.models import RTP
from filuta_fastapi_users.manager import BaseUserManager


class RefreshTokenManager(
    Generic[models.UP, models.ID, RTP]
):
    def __init__(
        self, 
        refresh_token_db = RefreshTokenDatabase[RTP],
    ):

        self.refresh_token_db = refresh_token_db
        
    def generate_refresh_token(self):
        return secrets.token_urlsafe()
        
        
    async def generate_new_token_for_user(self, user):
        token = self.generate_refresh_token()

        return await self.refresh_token_db.create(create_dict={
            "token": token,
            "user_id": user.id,
        })

    async def find_refresh_token(self, refresh_token: str = None, lifetime_seconds: int = None):
        
        max_age = None
        if lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=lifetime_seconds
            )
        
        return await self.refresh_token_db.get_by_token(token=refresh_token, max_age=max_age)

    async def delete_record(self, item):
        return await self.refresh_token_db.delete(refresh_token=item)