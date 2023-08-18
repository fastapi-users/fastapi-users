from filuta_fastapi_users.db.base import BaseUserDatabase, UserDatabaseDependency

__all__ = ["BaseUserDatabase", "UserDatabaseDependency"]


try:  # pragma: no cover
    from filuta_fastapi_users.filuta_uds import (  # noqa: F401
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