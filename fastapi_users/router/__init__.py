from fastapi_users.router.auth import get_auth_router  # noqa: F401
from fastapi_users.router.common import ErrorCode  # noqa: F401
from fastapi_users.router.register import get_register_router  # noqa: F401
from fastapi_users.router.reset import get_reset_password_router  # noqa: F401
from fastapi_users.router.users import get_users_router  # noqa: F401
from fastapi_users.router.verify import get_verify_router  # noqa: F401

try:
    from fastapi_users.router.oauth import get_oauth_router  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    pass
