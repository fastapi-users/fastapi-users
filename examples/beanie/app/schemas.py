from typing import Optional

from beanie import PydanticObjectId
from fastapi_users.schemas import (
    BaseUser,
    BaseUserCreate,
    BaseUserUpdate,
    ProtectedField,
    OrCond,
    AndCond,
    Requires,
    ActioningUser,
    TargetUser,
    Update,
)


class UserRead(BaseUser[PydanticObjectId]):
    """Organization User model."""

    organization: str = ""
    is_org_moderator: bool = False

    class Config:
        orm_mode = True


class UserCreate(BaseUserCreate):
    organization: Optional[
        ProtectedField(
            "Organization",
            str,
            OrCond(
                Requires(ActioningUser, "is_superuser", True),
                AndCond(
                    Requires(ActioningUser, "is_org_moderator", True),
                    Requires(Update, "organization", "$(ActioningUser).organization"),
                ),
            ),
        )
    ] = ""
    is_org_moderator: Optional[
        ProtectedField(
            "Is Organization Moderator",
            bool,
            OrCond(
                Requires(ActioningUser, "is_superuser", True),
                AndCond(
                    Requires(ActioningUser, "is_org_moderator", True),
                    Requires(Update, "organization", "$(ActioningUser).organization"),
                ),
            ),
        )
    ] = False


class UserUpdate(BaseUserUpdate):
    organization: ProtectedField(
        "Organization",
        str,
        AndCond(
            Requires(ActioningUser, "is_superuser", True),
            Requires(TargetUser, "organization", "$(ActioningUser).organization"),
        ),
    )
    is_org_moderator: Optional[
        ProtectedField(
            "Is Organization Moderator",
            bool,
            OrCond(
                Requires(ActioningUser, "is_superuser", True),
                AndCond(
                    Requires(ActioningUser, "is_org_moderator", True),
                    Requires(
                        TargetUser, "organization", "$(ActioningUser).organization"
                    ),
                ),
            ),
        )
    ]
