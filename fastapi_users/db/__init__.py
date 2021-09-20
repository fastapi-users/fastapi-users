from fastapi_users.db.base import BaseUserDatabase, UserDatabaseDependency  # noqa: F401

try:
    from fastapi_users_db_mongodb import MongoDBUserDatabase  # noqa: F401
except ImportError:  # pragma: no cover
    pass

try:
    from fastapi_users_db_sqlalchemy import (  # noqa: F401
        SQLAlchemyBaseOAuthAccountTable,
        SQLAlchemyBaseUserTable,
        SQLAlchemyUserDatabase,
    )
except ImportError:  # pragma: no cover
    pass

try:
    from fastapi_users_db_tortoise import (  # noqa: F401
        TortoiseBaseOAuthAccountModel,
        TortoiseBaseUserModel,
        TortoiseUserDatabase,
    )
except ImportError:  # pragma: no cover
    pass

try:
    from fastapi_users_db_ormar import (  # noqa: F401
        OrmarBaseOAuthAccountModel,
        OrmarBaseUserModel,
        OrmarUserDatabase,
    )
except ImportError:  # pragma: no cover
    pass
