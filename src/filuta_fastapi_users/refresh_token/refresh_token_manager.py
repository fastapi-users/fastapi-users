import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional
import random
from datetime import datetime, timedelta

from filuta_fastapi_users import exceptions, models
from filuta_fastapi_users.authentication.strategy.base import Strategy
from filuta_fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase,RefreshTokenDatabase, OtpTokenDatabase
from filuta_fastapi_users.authentication.strategy.db.models import OTPTP
from filuta_fastapi_users.manager import BaseUserManager


class RefreshTokenManager(
    Generic[models.UP, models.ID, OTPTP]
):
    def __init__(
        self, 
        otp_token_db = OtpTokenDatabase[OTPTP],
    ):

        self.otp_token_db = otp_token_db
        
    def generate_otp_token(self, length=6):
        """Generate a random OTP of given length."""
        # Generate OTP using numbers 0-9
        otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        return otp


    async def create_otp_token(self, access_token, mfa_token, mfa_type):
        
        current_datetime = datetime.utcnow()
        expire_time = current_datetime + timedelta(minutes=10)
        
        return await self.otp_token_db.create(create_dict={"access_token": access_token, "mfa_type": mfa_type, "mfa_token": mfa_token, "expire_at": expire_time})
    
    async def update_otp_token(self, otp_token_record, mfa_token):
        return await self.otp_token_db.update(otp_token=otp_token_record, update_dict={"mfa_token": mfa_token})

    async def find_otp_token(self, access_token, mfa_type, mfa_token, only_valid = False):
        return await self.otp_token_db.find_otp_token(access_token=access_token, mfa_type=mfa_type, mfa_token=mfa_token, only_valid=only_valid)

    async def user_has_issued_token(self, access_token, mfa_type):
        return await self.otp_token_db.user_has_token(access_token=access_token, mfa_type=mfa_type)

    async def delete_record(self, item):
        return await self.otp_token_db.delete(otp_token=item)