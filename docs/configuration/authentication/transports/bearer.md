# Bearer

With this transport, the token is expected inside the `Authorization` header of the HTTP request with the `Bearer` scheme. It's particularly suited for pure API interaction or mobile apps.

## Configuration

```py
from fastapi_users.authentication import BearerTransport

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
```

As you can see, instantiation is quite simple. It accepts the following arguments:

* `tokenUrl` (`str`): The exact path of your login endpoint. It'll allow the interactive documentation to automatically discover it and get a working *Authorize* button. In most cases, you'll probably need a **relative** path, not absolute. You can read more details about this in the [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/security/first-steps/#fastapis-oauth2passwordbearer).

## Login

This method will return the in the following form upon successful login:

!!! success "`200 OK`"
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
        "token_type": "bearer"
    }
    ```

> Check documentation about [login route](../../../usage/routes.md#post-login).

## Logout

The logout method with this transport returns nothing.

## Authentication

This method expects that you provide a `Bearer` authentication with a valid token corresponding to your strategy.

```bash
curl http://localhost:9000/protected-route -H'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI'
```
