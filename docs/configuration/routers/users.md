# Users router

This router provides routes to manage users. Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

SECRET = "SECRET"

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
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"],
)
```

### Optional: user verification

You can require the user to be **verified** (i.e. `is_verified` property set to `True`) to access those routes. You have to set the `requires_verification` parameter to `True` on the router instantiation method:

```py
app.include_router(
    fastapi_users.get_users_router(requires_verification=True),
    prefix="/users",
    tags=["users"],
)
```
