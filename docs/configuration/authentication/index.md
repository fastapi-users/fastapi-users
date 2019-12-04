# Authentication

**FastAPI Users** allows you to plug in several authentication methods.

## How it works?

You can have **several** authentication methods, e.g. a cookie authentication for browser-based queries and a JWT token authentication for pure API queries.

When checking authentication, each method is run one after the other. The first method yielding a user wins. If no method yields a user, an `HTTPException` is raised.

Each defined method will generate a [`/login/{name}`](../../usage/routes.md#post-loginname) route where `name` is defined on the authentication method object.

## Provided methods

* [JWT authentication](jwt.md)
* [Cookie authentication](cookie.md)
