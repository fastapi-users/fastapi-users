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

## In a path operation

If you don't need the user in the route logic, you can use this syntax:

```py
@app.get("/protected-route", dependencies=[Depends(current_superuser)])
def protected_route():
    return "Hello, some user."
```

You can read more about this [in FastAPI docs](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).
