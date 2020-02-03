# Router

We're almost there! The last step is to configure the `FastAPIUsers` object that will wire the database adapter, the authentication class and the user models to expose the FastAPI router.

## Configure `FastAPIUsers`

Configure `FastAPIUsers` object with all the elements we defined before. More precisely:

* `db`: Database adapter instance.
* `auth_backends`: List of authentication backends. See [Authentication](./authentication/index.md).
* `user_model`: Pydantic model of a user.
* `user_create_model`: Pydantic model for creating a user.
* `user_update_model`: Pydantic model for updating a user.
* `user_db_model`: Pydantic model of a DB representation of a user.
* `reset_password_token_secret`: Secret to encode reset password token.
* `reset_password_token_lifetime_seconds`: Lifetime of reset password token in seconds. Default to one hour.

```py
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
    SECRET,
)
```

And then, include the router in the FastAPI app:

```py
app = FastAPI()
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])
```

## Event handlers

In order to be as unopinionated as possible, we expose decorators that allow you to plug your own logic after some actions. You can have several handlers per event.

### After register

This event handler is called after a successful registration. It is called with **two argument**: the **user** that has just registered, and the original **`Request` object**.

Typically, you'll want to **send a welcome e-mail** or add it to your marketing analytics pipeline.

You can define it as an `async` or standard method.

Example:

```py
@fastapi_users.on_after_register()
def on_after_register(user: User, request: Request):
    print(f"User {user.id} has registered.")
```

### After forgot password

This event handler is called after a successful forgot password request. It is called with **three arguments**:

* The **user** which has requested to reset their password.
* A ready-to-use **JWT token** that will be accepted by the reset password route.
* The original **`Request` object**.

Typically, you'll want to **send an e-mail** with the link (and the token) that allows the user to reset their password.

You can define it as an `async` or standard method.

Example:

```py
@fastapi_users.on_after_forgot_password()
def on_after_forgot_password(user: User, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")
```

### After update

This event handler is called after a successful update user request. It is called with **three arguments**:

* The **user** which was updated.
* The dictionary containing the updated fields.
* The original **`Request` object**.

It may be useful if you wish for example update your user in a data analytics or customer success platform.

You can define it as an `async` or standard method.

Example:

```py
@fastapi_users.on_after_update()
def on_after_update(user: User, updated_user_data: Dict[str, Any], request: Request):
    print(f"User {user.id} has been updated with the following data: {updated_user_data}")
```

## Next steps

Check out a [full example](full_example.md) that will show you the big picture.
