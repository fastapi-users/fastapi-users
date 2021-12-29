import sys
from typing import Any, Dict, Union

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol  # pragma: no cover

from fastapi import Response
from fastapi.security.base import SecurityBase


class Transport(Protocol):
    scheme: SecurityBase

    async def get_login_response(self, token: str, response: Response) -> Any:
        ...  # pragma: no cover

    async def get_logout_response(self, response: Response) -> Any:
        ...  # pragma: no cover

    @staticmethod
    def get_openapi_login_responses_success() -> Dict[Union[int, str], Dict[str, Any]]:
        """Return a dictionary to use for the openapi responses route parameter."""
        ...  # pragma: no cover

    @staticmethod
    def get_openapi_logout_responses_success() -> Dict[Union[int, str], Dict[str, Any]]:
        """Return a dictionary to use for the openapi responses route parameter."""
        ...  # pragma: no cover
