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

### Optional: user verification

You can require the user to be **verified** (i.e. `is_verified` property set to `True`) to allow login. You have to set the `requires_validation` parameter to `True` on the router instantiation method:

```py
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication, requires_verification=True),
    prefix="/auth/jwt",
    tags=["auth"],
)
```
