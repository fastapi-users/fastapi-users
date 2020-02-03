# JWT

JSON Web Token (JWT) is an internet standard for creating access tokens based on JSON.

## Configuration

```py
from fastapi_users.authentication import JWTAuthentication

SECRET = "SECRET"

auth_backends = []

jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600))

auth_backends.append(jwt_authentication)
```

As you can see, instantiation is quite simple. You just have to define a constant `SECRET` which is used to encode the token and the lifetime of token (in seconds).

You can also optionally define the `name` which will be used to generate its [`/login` route](../../usage/routes.md#post-loginname). **Defaults to `jwt`**.

```py
jwt_authentication = JWTAuthentication(
    secret=SECRET,
    lifetime_seconds=3600,
    name="my-jwt",
)
```

## Login

This method will return a JWT token upon successful login:

!!! success "`200 OK`"
    ```json
    {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI"
    }
    ```

> Check documentation about [login route](../../usage/routes.md#post-loginname).

## Logout

This method is not applicable to this backend and won't do anything.

!!! success "`202 Accepted`"

> Check documentation about [logout route](../../usage/routes.md#post-logoutname).

## Authentication

This method expects that you provide a `Bearer` authentication with a valid JWT.

```bash
curl http://localhost:9000/protected-route -H'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI'
```

## Next steps

We will now configure the main **FastAPI Users** object that will expose the [API router](../router.md).
