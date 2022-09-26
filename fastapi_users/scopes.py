from enum import Enum
from typing import Union


class SystemScope(str, Enum):
    USER = "fastapi-users:user"
    SUPERUSER = "fastapi-users:superuser"
    VERIFIED = "fastapi-users:verified"
    REFRESH = "fastapi-users:refresh"

    def __str__(self) -> str:
        return self.value


UserDefinedScope = str
Scope = Union[SystemScope, UserDefinedScope]
