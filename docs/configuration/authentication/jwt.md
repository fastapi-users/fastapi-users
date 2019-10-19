# JWT

JSON Web Token (JWT) is an internet standard for creating access tokens based on JSON.

## Configuration

```py
from fastapi_users.authentication import JWTAuthentication

SECRET = "SECRET"

auth = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)
```

As you can see, instantiation is quite simple. You just have to define a constant `SECRET` which is used to encode the token and the lifetime of token (in seconds).

## Authentication

This method expects that you provide a `Bearer` authentication with a valid JWT.

```bash
curl http://localhost:9000/protected-route -H'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI'
```

{!./configuration/_next_router.md!}
