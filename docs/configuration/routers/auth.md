# Auth router

The auth router will generate `/login` and `/logout` (if applicable) routes for a given [authentication backend](../authentication/index.md).

Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

SECRET = "SECRET"

jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600))

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"],
)
```
