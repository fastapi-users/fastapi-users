# Dependency callables

**FastAPI Users** provides a dependency callable to easily inject authenticated user in your routes. They are available from your `FastAPIUsers` instance.

!!! tip
    For more information about how to make an authenticated request to your API, check the documentation of your [Authentication method](../configuration/authentication/index.md).

## `current_user`

Return a dependency callable to retrieve currently authenticated user, passing the following parameters:

* `optional`: If `True`, `None` is returned if there is no authenticated user or if it doesn't pass the other requirements. Otherwise, throw `401 Unauthorized`. Defaults to `False`.
* `active`: If `True`, throw `401 Unauthorized` if the authenticated user is inactive. Defaults to `False`.
* `verified`: If `True`, throw `401 Unauthorized` if the authenticated user is not verified. Defaults to `False`.
* `superuser`: If `True`, throw `403 Forbidden` if the authenticated user is not a superuser. Defaults to `False`.

### Examples

#### Get the current user (**active or not **)

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.current_user())):
    return f"Hello, {user.email}"
```

#### Get the current active user

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.current_user(active=True))):
    return f"Hello, {user.email}"
```

#### Get the current active and verified user

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    return f"Hello, {user.email}"
```

#### Get the current active superuser

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.current_user(active=True, superuser=True))):
    return f"Hello, {user.email}"
```

#### Reuse it

If you use it often, you can of course set it in a variable and reuse it at will:

```py
current_active_user = fastapi_users.current_user(active=True)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"
```

## Deprecated

!!! warning
    Those ones are still provided for backward compatibility but are deprecated and will be removed in a future release.

### `get_current_user`

Get the current user (**active or not**). Will throw a `401 Unauthorized` if missing or wrong credentials.

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.get_current_user)):
    return f"Hello, {user.email}"
```

### `get_current_active_user`

Get the current active user. Will throw a `401 Unauthorized` if missing or wrong credentials or if the user is not active.

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.get_current_active_user)):
    return f"Hello, {user.email}"
```

### `get_current_verified_user`

Get the current active and verified user. Will throw a `401 Unauthorized` if missing or wrong credentials or if the user is not active and verified.

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.get_current_verified_user)):
    return f"Hello, {user.email}"
```

### `get_current_superuser`

Get the current superuser. Will throw a `401 Unauthorized` if missing or wrong credentials or if the user is not active. Will throw a `403 Forbidden` if the user is not a superuser.

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.get_current_superuser)):
    return f"Hello, {user.email}"
```

### `get_current_verified_superuser`

Get the current verified superuser. Will throw a `401 Unauthorized` if missing or wrong credentials or if the user is not active and verified. Will throw a `403 Forbidden` if the user is not a superuser.

```py
@app.get("/protected-route")
def protected_route(user: User = Depends(fastapi_users.get_current_verified_superuser)):
    return f"Hello, {user.email}"
```

### `get_optional_current_user`

Get the current user (**active or not**). Will return `None` if missing or wrong credentials. It can be useful if you wish to change the behaviour of your endpoint if a user is logged in or not.

```py
@app.get("/optional-user-route")
def optional_user_route(user: Optional[User] = Depends(fastapi_users.get_optional_current_user)):
    if user:
        return f"Hello, {user.email}"
    else:
        return "Hello, anonymous"
```

### `get_optional_current_active_user`

Get the current active user. Will return `None` if missing or wrong credentials or if the user is not active. It can be useful if you wish to change the behaviour of your endpoint if a user is logged in or not.

```py
@app.get("/optional-user-route")
def optional_user_route(user: User = Depends(fastapi_users.get_optional_current_active_user)):
    if user:
        return f"Hello, {user.email}"
    else:
        return "Hello, anonymous"
```

### `get_optional_current_verified_user`

Get the current active and verified user. Will return `None` if missing or wrong credentials or if the user is not active and verified. It can be useful if you wish to change the behaviour of your endpoint if a user is logged in or not.

```py
@app.get("/optional-user-route")
def optional_user_route(user: User = Depends(fastapi_users.get_optional_current_verified_user)):
    if user:
        return f"Hello, {user.email}"
    else:
        return "Hello, anonymous"
```

### `get_optional_current_superuser`

Get the current superuser. Will return `None` if missing or wrong credentials or if the user is not active. It can be useful if you wish to change the behaviour of your endpoint if a user is logged in or not.

```py
@app.get("/optional-user-route")
def optional_user_route(user: User = Depends(fastapi_users.get_optional_current_superuser)):
    if user:
        return f"Hello, {user.email}"
    else:
        return "Hello, anonymous"
```

### `get_optional_current_verified_superuser`

Get the current active and verified superuser. Will return `None` if missing or wrong credentials or if the user is not active and verified. It can be useful if you wish to change the behaviour of your endpoint if a user is logged in or not.

```py
@app.get("/optional-user-route")
def optional_user_route(user: User = Depends(fastapi_users.get_optional_current_verified_superuser)):
    if user:
        return f"Hello, {user.email}"
    else:
        return "Hello, anonymous"
```

## In path operation

If you don't need the user in the route logic, you can use this syntax:

```py
@app.get("/protected-route", dependencies=[Depends(fastapi_users.get_current_superuser)])
def protected_route():
    return "Hello, some user."
```

You can read more about this [in FastAPI docs](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).
