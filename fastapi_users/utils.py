from datetime import datetime, timedelta

import jwt

JWT_ALGORITHM = "HS256"


def generate_jwt(
    data: dict, lifetime_seconds: int, secret: str, algorithm: str = JWT_ALGORITHM
) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=lifetime_seconds)
    payload["exp"] = expire
    return jwt.encode(payload, secret, algorithm=algorithm)
