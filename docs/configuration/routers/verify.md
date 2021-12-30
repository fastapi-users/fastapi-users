# Verify router

This router provides routes to manage user email verification. Check the [routes usage](../../usage/routes.md) to learn how to use them.

!!! success "👏👏👏"
    A big thank you to [Edd Salkield](https://github.com/eddsalkield) and [Mark Todd](https://github.com/mark-todd) who worked hard on this feature!

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
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
```
