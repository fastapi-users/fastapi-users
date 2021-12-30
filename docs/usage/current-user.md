# Get current user

**FastAPI Users** provides a dependency callable to easily inject authenticated user in your routes. They are available from your `FastAPIUsers` instance.

!!! tip
    For more information about how to make an authenticated request to your API, check the documentation of your [Authentication method](../configuration/authentication/index.md).

## `current_user`

Return a dependency callable to retrieve currently authenticated user, passing the following parameters:

* `optional`: If `True`, `None` is returned if there is no authenticated user or if it doesn't pass the other requirements. Otherwise, throw `401 Unauthorized`. Defaults to `False`.
* `active`: If `True`, throw `401 Unauthorized` if the authenticated user is inactive. Defaults to `False`.
* `verified`: If `True`, throw `403 Forbidden` if the authenticated user is not verified. Defaults to `False`.
* `superuser`: If `True`, throw `403 Forbidden` if the authenticated user is not a superuser. Defaults to `False`.
* `get_enabled_backends`: Optional dependency callable returning a list of enabled authentication backends. Useful if you want to dynamically enable some authentication backends based on external logic, like a configuration in database. By default, all specified authentication backends are enabled. *Please not however that every backends will appear in the OpenAPI documentation, as FastAPI resolves it statically.*

!!! tip "Create it once and reuse it"
    This function is a **factory**, a function returning another function 🤯

    It's this returned function that will be the dependency called by FastAPI in your API routes.

    To avoid having to generate it on each route and avoid issues when unit testing, it's **strongly recommended** that you assign the result in a variable and reuse it at will in your routes. The examples below demonstrate this pattern.

## Examples

### Get the current user (**active or not**)

```py
current_user = fastapi_users.current_user()

@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"
```

### Get the current **active** user

```py
current_active_user = fastapi_users.current_user(active=True)

@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"
```

### Get the current **active** and **verified** user

```py
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)

@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_verified_user)):
    return f"Hello, {user.email}"
```

### Get the current active **superuser**

```py
current_superuser = fastapi_users.current_user(active=True, superuser=True)

@app.get("/protected-route")
def protected_route(user: User = Depends(current_superuser)):
    return f"Hello, {user.email}"
```

### Dynamically enable authentication backends

!!! warning
    This is an advanced feature for cases where you have several authentication backends that are enabled conditionally. In most cases, you won't need this option.

```py
from fastapi import Request
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, CookieTransport, JWTStrategy

SECRET = "SECRET"

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
cookie_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

async def get_enabled_backends(request: Request):
    """Return the enabled dependencies following custom logic."""
    if request.url.path == "/protected-route-only-jwt":
        return [jwt_backend]
    else:
        return [cookie_backend, jwt_backend]


current_active_user = fastapi_users.current_user(active=True, get_enabled_backends=get_enabled_backends)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}. You are authenticated with a cookie or a JWT."


@app.get("/protected-route-only-jwt")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}. You are authenticated with a JWT."
```

## In a path operation

If you don't need the user in the route logic, you can use this syntax:

```py
@app.get("/protected-route", dependencies=[Depends(current_superuser)])
def protected_route():
    return "Hello, some user."
```

You can read more about this [in FastAPI docs](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).
