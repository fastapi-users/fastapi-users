# Auth router

The auth router will generate `/login` and `/logout` routes for a given [authentication backend](../authentication/index.md).

Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
```

### Optional: user verification

You can require the user to be **verified** (i.e. `is_verified` property set to `True`) to allow login. You have to set the `requires_verification` parameter to `True` on the router instantiation method:

```py
app.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    prefix="/auth/jwt",
    tags=["auth"],
)
```
