# Cookie

Cookies are an easy way to store stateful information into the user browser. Thus, it is more useful for browser-based navigation (e.g. a front-end app making API requests) rather than pure API interaction.

## Configuration

```py
from fastapi_users.authentication import CookieAuthentication

SECRET = "SECRET"

auth_backends = []

cookie_authentication = CookieAuthentication(secret=SECRET, lifetime_seconds=3600)

auth_backends.append(cookie_authentication)
```

As you can see, instantiation is quite simple. You just have to define a constant `SECRET` which is used to encode the token and the lifetime of the cookie (in seconds).

You can also define the parameters for the generated cookie:

* `cookie_name` (`fastapiusersauth`): Name of the cookie.
* `cookie_path` (`/`): Cookie path.
* `cookie_domain` (`None`): Cookie domain.
* `cookie_secure` (`True`): Whether to only send the cookie to the server via SSL request.
* `cookie_httponly` (`True`): Whether to prevent access to the cookie via JavaScript.
* `cookie_samesite` (`lax`): A string that specifies the samesite strategy for the cookie. Valid values are 'lax', 'strict' and 'none'. Defaults to 'lax'. 

!!! tip
    You can also optionally define the `name`. It's useful in the case you wish to have several backends of the same class. Each backend should have a unique name. **Defaults to `cookie`**.

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

## Logout

This method will remove the authentication cookie:

!!! success "`200 OK`"

> Check documentation about [logout route](../../usage/routes.md#post-logoutname).

## Authentication

This method expects that you provide a valid cookie in the headers.

## Next steps

We will now configure the main **FastAPI Users** object that will expose the [routers](../routers/index.md).
