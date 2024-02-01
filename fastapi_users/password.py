import secrets
from typing import Protocol, Tuple

import bcrypt


class PasswordHelperProtocol(Protocol):
    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> Tuple[bool, str]: ...  # pragma: no cover

    def hash(self, password: str) -> str: ...  # pragma: no cover

    def generate(self) -> str: ...  # pragma: no cover


class PasswordHelper(PasswordHelperProtocol):
    def __init__(self, salt_rounds: int = 12) -> None:
        self.salt_rounds = salt_rounds

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> Tuple[bool, str]:
        hashed_bytes = hashed_password.encode("utf-8")
        plain_bytes = plain_password.encode("utf-8")

        if bcrypt.checkpw(plain_bytes, hashed_bytes):
            return True, hashed_password
        else:
            new_hashed_password = self.hash(plain_password)
            return False, new_hashed_password

    def hash(self, password: str) -> str:
        hashed_bytes = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(self.salt_rounds)
        )
        return hashed_bytes.decode("utf-8")

    def generate(self) -> str:
        return secrets.token_urlsafe()
