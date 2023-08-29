import secrets
from datetime import datetime, timedelta
from typing import Generic

from filuta_fastapi_users import models
from filuta_fastapi_users.authentication.strategy.db.adapter import OtpTokenDatabase
from filuta_fastapi_users.types import DependencyCallable


class OtpManager(Generic[models.OTPTP]):
    def __init__(
        self,
        otp_token_db: OtpTokenDatabase[models.OTPTP],
    ) -> None:
        self.otp_token_db = otp_token_db

    def generate_otp_token(self, length: int = 6) -> str:
        """Generate a random OTP of given length."""
        # Generate OTP using numbers 0-9
        otp = "".join([str(secrets.randbelow(10)) for _ in range(length)])
        return otp

    async def create_otp_email_token(self, access_token: str, mfa_token: str) -> models.OTPTP:
        otp_record = await self.otp_token_db.create(
            {"access_token": access_token, "mfa_type": "email", "mfa_token": mfa_token}
        )
        return otp_record

    async def create_otp_token(self, access_token: str, mfa_token: str, mfa_type: str) -> models.OTPTP:
        current_datetime = datetime.utcnow()
        expire_time = current_datetime + timedelta(minutes=10)

        return await self.otp_token_db.create(
            {
                "access_token": access_token,
                "mfa_type": mfa_type,
                "mfa_token": mfa_token,
                "expire_at": expire_time,
            }
        )

    async def update_otp_token(self, otp_token_record: models.OTPTP, mfa_token: str) -> models.OTPTP:
        return await self.otp_token_db.update(otp_token_record, {"mfa_token": mfa_token})

    async def find_otp_token(
        self, access_token: str, mfa_type: str, mfa_token: str, only_valid: bool = False
    ) -> models.OTPTP | None:
        return await self.otp_token_db.find_otp_token(access_token, mfa_type, mfa_token, only_valid)

    async def user_has_issued_token(self, access_token: str, mfa_type: str) -> models.OTPTP | None:
        return await self.otp_token_db.user_has_token(access_token, mfa_type)

    async def delete_record(self, otp_record: models.OTPTP) -> None:
        return await self.otp_token_db.delete(otp_record)


OtpManagerDependency = DependencyCallable[OtpManager[models.OTPTP]]
