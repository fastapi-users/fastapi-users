import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional
import random

from filuta_fastapi_users import exceptions, models
from filuta_fastapi_users.authentication.strategy.base import Strategy
from filuta_fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase,RefreshTokenDatabase, OtpTokenDatabase
from filuta_fastapi_users.authentication.strategy.db.models import OTPTP
from filuta_fastapi_users.manager import BaseUserManager


class OtpManager(
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


    async def create_otp_email_token(self, access_token, mfa_token):
        otp_record = await self.otp_token_db.create(create_dict={"access_token": access_token, "mfa_type": "email", "mfa_token": mfa_token})
        return otp_record


    async def find_otp_token(self, access_token, mfa_type, mfa_token):
        otp_record = await self.otp_token_db.find_otp_token(access_token=access_token, mfa_type=mfa_type, mfa_token=mfa_token)
        return otp_record