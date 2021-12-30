# 8.x.x ➡️ 9.x.x

Version 9 revamps the authentication backends: we splitted the logic of a backend into two: the **transport**, which is how the token will be carried over the request and the **strategy**, which is how the token is generated and secured.

The benefit of this is that we'll soon be able to propose new strategies, like database session tokens, without having to repeat the transport logic which remains the same.

## Convert the authentication backend

You now have to generate an authentication backend with a transport and a strategy.

### I used JWTAuthentication

=== "Before"

    ```py
    from fastapi_users.authentication import JWTAuthentication

    jwt_authentication = JWTAuthentication(
        secret=SECRET, lifetime_seconds=3600, tokenUrl="auth/jwt/login"
    )
    ```

=== "After"

    ```py
    from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

    SECRET = "SECRET"

    bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

    def get_jwt_strategy() -> JWTStrategy:
        return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

    auth_backend = AuthenticationBackend(
        name="jwt",
        transport=bearer_transport,
        get_strategy=get_jwt_strategy,
    )
    ```

!!! warning
    There is no default `name` anymore: you need to provide it yourself for each of your backends.

### I used CookieAuthentication

=== "Before"

    ```py
    from fastapi_users.authentication import CookieAuthentication

    cookie_authentication = CookieAuthentication(secret=SECRET, lifetime_seconds=3600)
    ```

=== "After"

    ```py
    from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy

    SECRET = "SECRET"

    cookie_transport = CookieTransport(cookie_max_age=3600)

    def get_jwt_strategy() -> JWTStrategy:
        return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

    auth_backend = AuthenticationBackend(
        name="cookie",
        transport=cookie_transport,
        get_strategy=get_jwt_strategy,
    )
    ```

!!! warning
    There is no default `name` anymore: you need to provide it yourself for each of your backends.

!!! tip
    Notice that the strategy is the same for both authentication backends. That's the beauty of this approach: the token generation is decoupled from its transport.

## OAuth: one router for each backend

Before, a single OAuth router was enough to login with any of your authentication backend. Now, you need to generate a router for each of your backends.

=== "Before"

    ```py
    app.include_router(
        fastapi_users.get_oauth_router(google_oauth_client, "SECRET"),
        prefix="/auth/google",
        tags=["auth"],
    )
    ```

=== "After"

    ```py
    app.include_router(
        fastapi_users.get_oauth_router(google_oauth_client, auth_backend, "SECRET"),
        prefix="/auth/google",
        tags=["auth"],
    )
    ```

### `authentication_backend` is not needed on `/authorize`

The consequence of this is that you don't need to specify the authentication backend when making a request to `/authorize`.


=== "Before"

    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -X GET \
    http://localhost:8000/auth/google/authorize?authentication_backend=jwt
    ```

=== "After"

    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -X GET \
    http://localhost:8000/auth/google/authorize
    ```

## Lost?

If you're unsure or a bit lost, make sure to check the [full working examples](../configuration/full-example.md).
