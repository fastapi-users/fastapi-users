# Cookie

Cookies are an easy way to store stateful information into the user browser. Thus, it is more useful for browser-based navigation (e.g. a front-end app making API requests) rather than pure API interaction.

## Configuration

```py
from fastapi_users.authentication import CookieTransport

cookie_transport = CookieTransport(cookie_max_age=3600)
```

As you can see, instantiation is quite simple. It accepts the following arguments:

* `cookie_name` (`fastapiusersauth`): Name of the cookie.
* `cookie_max_age` (`Optional[int]`): The lifetime of the cookie in seconds. `None` by default, which means it's a session cookie.
* `cookie_path` (`/`): Cookie path.
* `cookie_domain` (`None`): Cookie domain.
* `cookie_secure` (`True`): Whether to only send the cookie to the server via SSL request.
* `cookie_httponly` (`True`): Whether to prevent access to the cookie via JavaScript.
* `cookie_samesite` (`lax`): A string that specifies the samesite strategy for the cookie. Valid values are `lax`, `strict` and `none`. Defaults to `lax`.

## Login

This method will return a response with a valid `set-cookie` header upon successful login:

!!! success "`200 OK`"

> Check documentation about [login route](../../../usage/routes.md#post-login).

## Logout

This method will remove the authentication cookie:

!!! success "`200 OK`"

> Check documentation about [logout route](../../../usage/routes.md#post-logout).

## Authentication

This method expects that you provide a valid cookie in the headers.
