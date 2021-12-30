# Authentication

**FastAPI Users** allows you to plug in several authentication methods.

## How it works?

You can have **several** authentication methods, e.g. a cookie authentication for browser-based queries and a JWT token authentication for pure API queries.

When checking authentication, each method is run one after the other. The first method yielding a user wins. If no method yields a user, an `HTTPException` is raised.

For each backend, you'll be able to add a router with the corresponding `/login` and `/logout` (if applicable routes). More on this in the [routers documentation](../routers/index.md).

## Transport + Strategy = Authentication backend

An authentication backend is composed of two parts:

### Transport

It manages how the token will be carried over the request. We currently provide two methods:

* [Cookie](transports/cookie.md): the token will be send through a cookie.
* [Bearer](transports/bearer.md): the token will be send through an `Authorization: Bearer` header.

### Strategy

It manages how the token is generated and secured. We currently provide one method:

* [JWT](strategy/jwt.md): the token is self-contained in a JSON Web Token.
