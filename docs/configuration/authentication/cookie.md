# Cookie

Cookies are an easy way to store stateful information into the user browser. Thus, it is more useful for browser-based navigation (e.g. a front-end app making API requests) rather than pure API interaction.

## Configuration

```py
from fastapi_users.authentication import CookieAuthentication

SECRET = "SECRET"

auth_backends = []

cookie_authentication = CookieAuthentication(secret=SECRET, lifetime_seconds=3600))

auth_backends.append(cookie_authentication)
```

As you can see, instantiation is quite simple. You just have to define a constant `SECRET` which is used to encode the token and the lifetime of the cookie (in seconds).

You can optionally define the `cookie_name`. **Defaults to `fastapiusersauth`**.

You can also optionally define the `name` which will be used to generate its [`/login` route](../../usage/routes.md#post-loginname). **Defaults to `cookie`**.

```py
cookie_authentication = CookieAuthentication(
    secret=SECRET,
    lifetime_seconds=3600,
    name="my-cookie",
)
```

!!! tip
    The value of the cookie is actually a JWT. This authentication backend shares most of its logic with the [JWT](./jwt.md) one.

## Login

This method will return a response with a valid `set-cookie` header upon successful login:

!!! success "`200 OK`"

> Check documentation about [login route](../../usage/routes.md#post-loginname).

## Authentication

This method expects that you provide a valid cookie in the headers.

## Next steps

We will now configure the main **FastAPI Users** object that will expose the [API router](../router.md).
