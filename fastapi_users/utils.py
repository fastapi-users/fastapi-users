from datetime import datetime, timedelta
from typing import Optional

import jwt

JWT_ALGORITHM = "HS256"


def generate_jwt(
    data: dict,
    secret: str,
    lifetime_seconds: Optional[int] = None,
    algorithm: str = JWT_ALGORITHM,
) -> str:
    payload = data.copy()
    if lifetime_seconds:
        expire = datetime.utcnow() + timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
    return jwt.encode(payload, secret, algorithm=algorithm)
