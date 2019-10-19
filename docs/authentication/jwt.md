# JWT

JSON Web Token (JWT) is an internet standard for creating access tokens based on JSON.

## Configuration

```py
from fastapi_users.authentication import JWTAuthentication

SECRET = "SECRET"

auth = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)
```

As you can see, instantiation is quite simple. You just have to define a constant `SECRET` which is used to encode the token and the lifetime of token (in seconds).

{!./_next_router.md!}
