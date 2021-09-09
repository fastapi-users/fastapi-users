# JWT

JSON Web Token (JWT) is an internet standard for creating access tokens based on JSON.

## Configuration

```py
from fastapi_users.authentication import JWTAuthentication

SECRET = "SECRET"

auth_backends = []

jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600, tokenUrl="auth/jwt/login")

auth_backends.append(jwt_authentication)
```

As you can see, instantiation is quite simple. It accepts the following arguments:

* `secret` (`Union[str, pydantic.SecretStr]`): A constant secret which is used to encode the token. **Use a strong passphrase and keep it secure.**
* `lifetime_seconds` (`int`): The lifetime of the token in seconds.
* `tokenUrl` (`Optional[str]`): The exact path of your login endpoint. It'll allow the interactive documentation to automatically discover it and get a working *Authorize* button. In most cases, you'll probably need a **relative** path, not absolute. You can read more details about this in the [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/security/first-steps/#fastapis-oauth2passwordbearer). Defaults to `auth/jwt/login`.
* `name` (`Optional[str]`): Name of the backend. It's useful in the case you wish to have several backends of the same class. Each backend should have a unique name. Defaults to `jwt`.

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
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
        "token_type": "bearer"
    }
    ```

> Check documentation about [login route](../../usage/routes.md#post-loginname).

## Logout

This backend does not provide a logout method (a JWT is valid until it expires).

## Authentication

This method expects that you provide a `Bearer` authentication with a valid JWT.

```bash
curl http://localhost:9000/protected-route -H'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI'
```

## Tip: Refresh

The default implementation **does not** provide a mechanism to refresh the JWT. However, you can implement it quite easily like this:

```py
from fastapi import Depends, Response


@router.post("/auth/jwt/refresh")
async def refresh_jwt(response: Response, user=Depends(fastapi_users.current_user(active=True))):
    return await jwt_authentication.get_login_response(user, response)
```

## Next steps

We will now configure the main **FastAPI Users** object that will expose the [routers](../routers/index.md).
