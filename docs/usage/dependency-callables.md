# Dependency callables

**FastAPI Users** provides dependency callables to easily inject users in your routes. They are available from your `FastAPIUsers` instance.

!!! tip
    For more information about how to make an authenticated request to your API, check the documentation of your [Authentication method](../configuration/authentication/index.md).

## `get_current_user`

Get the current user (**active or not**). Will throw a `401 Unauthorized` if missing or wrong credentials.

```py
@app.get('/protected-route')
def protected_route(user: User = Depends(fastapi_users.get_current_user)):
    return f'Hello, {user.email}'
```

## `get_current_active_user`

Get the current active user. Will throw a `401 Unauthorized` if missing or wrong credentials or if the user is not active.

```py
@app.get('/protected-route')
def protected_route(user: User = Depends(fastapi_users.get_current_active_user)):
    return f'Hello, {user.email}'
```

## `get_current_superuser`

Get the current superuser. Will throw a `401 Unauthorized` if missing or wrong credentials or if the user is not active. Will throw a `403 Forbidden` if the user is not a superuser.

```py
@app.get('/protected-route')
def protected_route(user: User = Depends(fastapi_users.get_current_superuser)):
    return f'Hello, {user.email}'
```

## In path operation

If you don't need a user, you can use more clear way:

```py
@app.get('/protected-route', dependencies=[Depends(fastapi_users.get_current_superuser)])
def protected_route():
    return 'Hello, some user.'
```

You can read more about this [in FastAPI docs](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).
