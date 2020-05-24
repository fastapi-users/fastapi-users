# Users router

This router provides routes to manage users. Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
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

## After update

You can provide a custom function to be called after a successful update user request. It is called with **three arguments**:

* The **user** which was updated.
* The dictionary containing the updated fields.
* The original **`Request` object**.

It may be useful if you wish for example update your user in a data analytics or customer success platform.

You can define it as an `async` or standard method.

Example:

```py
def on_after_update(user: UserDB, updated_user_data: Dict[str, Any], request: Request):
    print(f"User {user.id} has been updated with the following data: {updated_user_data}")

app.include_router(
    fastapi_users.get_users_router(on_after_update),
    prefix="/users",
    tags=["users"],
)
```
