from fastapi_users.db.base import BaseUserDatabase, UserDatabaseDependency

__all__ = [
    "BaseUserDatabase",
    "UserDatabaseDependency",
]

try:  # pragma: no cover
    from fastapi_users_db_mongodb import MongoDBUserDatabase  # noqa: F401

    __all__.append("MongoDBUserDatabase")
except ImportError:  # pragma: no cover
    pass

try:  # pragma: no cover
    from fastapi_users_db_sqlalchemy import (  # noqa: F401
        SQLAlchemyBaseOAuthAccountTable,
        SQLAlchemyBaseUserTable,
        SQLAlchemyUserDatabase,
    )

    __all__.append("SQLAlchemyBaseOAuthAccountTable")
    __all__.append("SQLAlchemyBaseUserTable")
    __all__.append("SQLAlchemyUserDatabase")
except ImportError:  # pragma: no cover
    pass

try:  # pragma: no cover
    from fastapi_users_db_tortoise import (  # noqa: F401
        TortoiseBaseOAuthAccountModel,
        TortoiseBaseUserModel,
        TortoiseUserDatabase,
    )

    __all__.append("TortoiseBaseOAuthAccountModel")
    __all__.append("TortoiseBaseUserModel")
    __all__.append("TortoiseUserDatabase")
except ImportError:  # pragma: no cover
    pass

try:  # pragma: no cover
    from fastapi_users_db_ormar import (  # noqa: F401
        OrmarBaseOAuthAccountModel,
        OrmarBaseUserModel,
        OrmarUserDatabase,
    )

    __all__.append("OrmarBaseOAuthAccountModel")
    __all__.append("OrmarBaseUserModel")
    __all__.append("OrmarUserDatabase")
except ImportError:  # pragma: no cover
    pass
