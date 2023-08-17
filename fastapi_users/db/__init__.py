from fastapi_users.db.base import BaseUserDatabase, UserDatabaseDependency

__all__ = ["BaseUserDatabase", "UserDatabaseDependency"]


try:  # pragma: no cover
    from fastapi_users_db_sqlalchemy import (  # noqa: F401
        SQLAlchemyBaseOAuthAccountTable,
        SQLAlchemyBaseOAuthAccountTableUUID,
        SQLAlchemyBaseUserTable,
        SQLAlchemyBaseUserTableUUID,
        SQLAlchemyUserDatabase,
    )

    __all__.append("SQLAlchemyBaseUserTable")
    __all__.append("SQLAlchemyBaseUserTableUUID")
    __all__.append("SQLAlchemyBaseOAuthAccountTable")
    __all__.append("SQLAlchemyBaseOAuthAccountTableUUID")
    __all__.append("SQLAlchemyUserDatabase")
except ImportError:  # pragma: no cover
    pass

try:  # pragma: no cover
    from fastapi_users_db_beanie import (  # noqa: F401
        BaseOAuthAccount,
        BeanieBaseUser,
        BeanieUserDatabase,
        ObjectIDIDMixin,
    )

    __all__.append("BeanieBaseUser")
    __all__.append("BaseOAuthAccount")
    __all__.append("BeanieUserDatabase")
    __all__.append("ObjectIDIDMixin")
except ImportError:  # pragma: no cover
    pass

try:  # pragma: no cover
    from fastapi_users_db_sqlmodel import (  # noqa: F401
        SQLModelBaseUserDB,
        SQLModelBaseOAuthAccount,
        SQLModelUserDatabase,
        SQLModelUserDatabaseAsync,
    )

    __all__.append("SQLModelBaseUserDB")
    __all__.append("SQLModelBaseOAuthAccount")
    __all__.append("SQLModelUserDatabase")
    __all__.append("SQLModelUserDatabaseAsync")
except ImportError:  # pragma: no cover
    pass
