# Register routes

The register router will generate a `/register` route to allow a user to create a new account, and optionally an `/activate` route to allow activation of the user account. 

Check the [routes usage](../../usage/routes.md) to learn how to use them.

## User activation

Each user account has an associated `is_active` attribute.  This determines whether or not the user is activated.  Only activated users can log in and request a password reset.  Check the [user model](../../configuration/model.md) to learn more about the attributes of a user.

By default, any users created by calling the `/register` route are activated upon initialisation.

If user verification is required, then the `activation_callback` must be supplied to `get_register_router`, the register router generator. When this callback is supplied, newly registered users are not activated by default, and a corresponding `/activate` route is created.

User activation then proceeds as follows:

* The user registers using the `/register` route.
* The `activation_callback` is called, with a unique activation token in the request body.
* The user is activated if this token is supplied as a parameter to the `/activate` route before token expiry (after `activation_token_lifetime_seconds`).
* Finally, the `after_register` callback is called once the user is activated.

Email verification can be implemented within `activation_callback`, emailing the user with the corresponding `/activate` URL.  An example can be found [below](#activation-callback).

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
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)

```
`get_register_router`

Parameters:

* `after_register: Optional[Callable[[models.UD, Request], None]] = None`

    Optional callback which takes a **user** (`models.UD`) and a **request** (`Request`) and is called upon user activation.

* `activation_callback: Optional[Callable[[models.UD, str, Request], None]] = None`

    Optional callback which takes a **user** (`models.UD`), a **token** (`str`) and a **request** (`Request`). If supplied, the user is not activated by default, and can be activated by passing the token to the activate route. If not supplied, no activation step occurs and the user is activated by default.

* `activation_token_secret: str = None`: 

    Cryptographic secret to encode activation token. Required if `activation_callback` supplied.

* `activation_token_lifetime_seconds: int = 3600`:

    Lifetime of the activation token in seconds, if activation_callback supplied. **Defaults to 3600**.

## After register callback

You can provide a custom function, `after_register` to be called after a user is successfully activated. This can occur either upon registration if no `activation_callback` is specified, or instead upon activation otherwise. This is called with **two arguments**:

* The `user` that has just registered
* The original `Request` object

Typically, you'll want to **send a welcome e-mail** or add it to your marketing analytics pipeline.

You can define it as an `async` or standard method.

Example:

```py
def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")

app.include_router(
    fastapi_users.get_register_router(on_after_register),
    prefix="/auth",
    tags=["auth"],
)
```

## Activation callback

You can optionally provide an `activation_callback` for [custom user activation](#user-activation). It is called with **three arguments**:

* The `user` that has just registered
* The activation `token` associated with that user
* The original `Request` object

You must also supply `activation_token_secret` for this case - a cryptographic secret used to sign the token.

`get_register_router` automatically initializes the `/activate` route when `activation_token_secret` and `activation_callback` are supplied.

A token will be passed to your `activation_callback`. This token can be used to create a url to the `/activate` router, which will in turn activate a user.

Typically, you'll want to **send an activation e-mail** which contains this URL.

Example:

```py
def activation_callback(
    created_user: Type[models.BaseUserCreate],
    token: str,
    request: Request
):
    confirm_url = request.url_for("activate", token=token)
    print('User {user.id} is to be activated. Visit {confirm_url} to activate.')

def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")

app.include_router(
    fastapi_users.get_register_router(
        after_register = on_after_register,
        activation_callback = activation_callback,
        activation_token_secret = 'teststring'
    ), prefix="/auth", tags=["auth"]
)
```
