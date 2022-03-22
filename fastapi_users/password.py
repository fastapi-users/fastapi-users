from functools import lru_cache
from typing import Tuple, Optional

from passlib import pwd
from passlib.context import CryptContext


@lru_cache()
def get_crypt_context(**crypt_context_kwargs):
    if crypt_context_kwargs:
        if "schemes" not in crypt_context_kwargs:
            crypt_context_kwargs["schemes"] = ["bcrypt"]
        if "deprecated" not in crypt_context_kwargs:
            crypt_context_kwargs["deprecated"] = ["auto"]
        return CryptContext(**crypt_context_kwargs)
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_and_update_password(
    plain_password: str, hashed_password: str, crypt_context: Optional[CryptContext] = None
) -> Tuple[bool, str]:
    crypt_context = crypt_context or get_crypt_context()
    return crypt_context.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str, crypt_context: Optional[CryptContext] = None) -> str:
    crypt_context = crypt_context or get_crypt_context()
    return crypt_context.hash(password)


def generate_password() -> str:
    return pwd.genword()
