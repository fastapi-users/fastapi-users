# Overview

The schema below shows you how the library is structured and how each part fit together.


```mermaid
flowchart TB
    FASTAPI_USERS{FastAPIUsers}
    USER_MANAGER{UserManager}
    USER_MODEL{User model}
    DATABASE_DEPENDENCY[[get_user_db]]
    USER_MANAGER_DEPENDENCY[[get_user_manager]]
    CURRENT_USER[[current_user]]
    subgraph SCHEMAS[Schemas]
        USER[User]
        USER_CREATE[UserCreate]
        USER_UPDATE[UserUpdate]
    end
    subgraph DATABASE[Database adapters]
        SQLALCHEMY[SQLAlchemy]
        BEANIE[Beanie]
    end
    subgraph ROUTERS[Routers]
        AUTH[[get_auth_router]]
        OAUTH[[get_oauth_router]]
        REGISTER[[get_register_router]]
        VERIFY[[get_verify_router]]
        RESET[[get_reset_password_router]]
        USERS[[get_users_router]]
    end
    subgraph AUTH_BACKENDS[Authentication]
        subgraph TRANSPORTS[Transports]
            COOKIE[CookieTransport]
            BEARER[BearerTransport]
        end
        subgraph STRATEGIES[Strategies]
            DB[DatabaseStrategy]
            JWT[JWTStrategy]
            REDIS[RedisStrategy]
        end
        AUTH_BACKEND{AuthenticationBackend}
    end
    DATABASE --> DATABASE_DEPENDENCY
    USER_MODEL --> DATABASE_DEPENDENCY
    DATABASE_DEPENDENCY --> USER_MANAGER

    USER_MANAGER --> USER_MANAGER_DEPENDENCY
    USER_MANAGER_DEPENDENCY --> FASTAPI_USERS

    FASTAPI_USERS --> ROUTERS

    TRANSPORTS --> AUTH_BACKEND
    STRATEGIES --> AUTH_BACKEND

    AUTH_BACKEND --> ROUTERS
    AUTH_BACKEND --> FASTAPI_USERS

    FASTAPI_USERS --> CURRENT_USER

    SCHEMAS --> ROUTERS
```

## User model and database adapters

FastAPI Users is compatible with various **databases and ORM**. To build the interface between those database tools and the library, we provide database adapters classes that you need to instantiate and configure.

➡️ [I'm using SQLAlchemy](databases/sqlalchemy.md)

➡️ [I'm using Beanie](databases/beanie.md)

## Authentication backends

Authentication backends define the way users sessions are managed in your app, like access tokens or cookies.

They are composed of two parts: a **transport**, which is how the token will be carried over the requests (e.g. cookies, headers...) and a **strategy**, which is how the token will be generated and secured (e.g. a JWT, a token in database...).

➡️ [Configure the authentication backends](./authentication/index.md)

## `UserManager`

The `UserManager` object bears most of the logic of FastAPI Users: registration, verification, password reset... We provide a `BaseUserManager` with this common logic; which you should overload to define how to validate passwords or handle events.

This `UserManager` object should be provided through a FastAPI dependency, `get_user_manager`.

➡️ [Configure `UserManager`](./user-manager.md)

## Schemas

FastAPI is heavily using [Pydantic models](https://pydantic-docs.helpmanual.io/) to validate request payloads and serialize responses. **FastAPI Users** is no exception and will expect you to provide Pydantic schemas representing a user when it's read, created and updated.

➡️ [Configure schemas](./schemas.md)

## `FastAPIUsers` and routers

Finally, `FastAPIUsers` object is the main class from which you'll be able to generate routers for classic routes like registration or login, but also get the `current_user` dependency factory to inject the authenticated user in your own routes.

➡️ [Configure `FastAPIUsers` and routers](./routers/index.md)
