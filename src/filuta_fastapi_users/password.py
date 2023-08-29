from typing import Protocol

from passlib import pwd
from passlib.context import CryptContext


class PasswordHelperProtocol(Protocol):
    def verify_and_update(self, plain_password: str, hashed_password: str) -> tuple[bool, str]:
        ...  # pragma: no cover

    def hash(self, password: str) -> str:
        ...  # pragma: no cover

    def generate(self) -> str:
        ...  # pragma: no cover


class PasswordHelper(PasswordHelperProtocol):
    def __init__(self, context: CryptContext | None = None) -> None:
        if context is None:
            self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        else:
            self.context = context  # pragma: no cover

    def verify_and_update(self, plain_password: str, hashed_password: str) -> tuple[bool, str]:
        return self.context.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.context.hash(password)

    def generate(self) -> str:
        return pwd.genword()
