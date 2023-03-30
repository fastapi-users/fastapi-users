import types
import typing
from typing import (
    Callable,
    ClassVar,
    Generic,
    List,
    NewType,
    Optional,
    TypeVar,
    Any,
    Type,
    Dict,
    Tuple,
    Union,
)
import re

from pydantic import BaseModel, EmailStr, ValidationError, validate_model
from pydantic.env_settings import InitSettingsSource
from pydantic.fields import ModelField

from fastapi import HTTPException, status
from fastapi_users import models
from fastapi_users.exceptions import UnauthorizedUpdateException


T = TypeVar("T")


class _Condition:
    Unary = 1
    Binary = 2


class Condition(BaseModel, _Condition):
    """
    This class represents a condition that needs to be fulfilled.
    It holds a lambda that upon __call__ is executed and returns a bool.
    The logic for the condition is held inside tha lambda and it will be
        implemented by the function that returns a Condition object.
    See: Requires, OrCond, AndCond
    """

    predicate: Optional[Callable] = None

    """
    If the condition is a binary operator it returns: [Unary, operator, cond_1, cond_2]
    If the condition is a unary operator it returns: [Binary, condition_desc]
    Implementations reside in different functions that return Conditions.
    """
    doc: Optional[
        Callable[
            "Condition", Tuple[int, Union[Tuple[str, "Condition", "Condition"], str]]
        ]
    ] = None

    def __call__(self, *args, **kwargs) -> bool:
        assert self.predicate, "predicate should never be None"
        return self.predicate and self.predicate(*args, **kwargs)


def get_condition_doc(root: Condition) -> str:
    """
    Helper function that traverses through the condition tree and creates a
        human readable documentation and returns it as a string.
    """

    op_typ, doc_ret = root.doc(root)

    if op_typ == Condition.Unary:
        return doc_ret

    op, left, right = doc_ret
    return f"({get_condition_doc(left)} {op} {get_condition_doc(right)})"


TargetUser = "TargetUser"
ActioningUser = "ActioningUser"
Update = "Update"


def Requires(
    subject_user: str, field_name: Optional[str], field_value: Any = None
) -> Condition:
    def predicate(
        subject_user: str,
        field_name: Optional[str],
        field_value: Any,
        actioning_user: Any,
        target_user: Any,
        update_obj: Any,
    ) -> bool:
        obj: Any
        if subject_user == TargetUser:
            obj = target_user
        elif subject_user == ActioningUser:
            obj = actioning_user
        elif subject_user == Update:
            obj = update_obj
        else:
            assert False, (
                f"subject_user has to be either"
                f"TargetUser('{TargetUser}') or"
                f"ActioningUser('{ActioningUser}')"
                f"Update('{Update}')"
            )

        if not field_name:
            return obj is None

        if isinstance(field_value, str):
            field_key: str
            field_ref_obj: Optional[Any] = None
            if f"$({ActioningUser})" in field_value:
                field_key = field_value[len(f"$({ActioningUser})") + 1 :]
                field_ref_obj = actioning_user
            elif f"$({TargetUser})" in field_value:
                field_key = field_value[len(f"$({TargetUser})") + 1 :]
                field_ref_obj = target_user
            elif f"$({Update})" in field_value:
                field_key = field_value[len(f"$({Update})") + 1 :]
                field_ref_obj = update_obj
            else:
                field_key = field_value

            if field_key != field_value:
                if not field_ref_obj:
                    return False
                _field_value_resolved = field_ref_obj.dict()[field_key]
                field_value = _field_value_resolved

        return hasattr(obj, field_name) and getattr(obj, field_name) == field_value

    c = Condition()
    c.predicate = lambda actioning_user, target_user, update_obj, subject_user=subject_user, field_name=field_name, field_value=field_value: predicate(
        subject_user, field_name, field_value, actioning_user, target_user, update_obj
    )

    def doc(self) -> Tuple[int, Union[Tuple[str, Condition, Condition], str]]:
        doc_field_value: str
        if isinstance(field_value, str):
            doc_field_value = re.sub(r"\$\((.*)\)", r"\1", field_value)
        else:
            doc_field_value = field_value
        return (Condition.Unary, f"{subject_user}.{field_name} == {doc_field_value}")

    c.doc = doc

    return c


def AndCond(p: Condition, q: Condition) -> Condition:
    def predicate(p: Condition, q: Condition, *args, **kwargs):
        b1 = p(*args, **kwargs)
        b2 = q(*args, **kwargs)
        return b1 and b2

    c = Condition()
    c.predicate = lambda *args, p=p, q=q: predicate(p, q, *args)

    def doc(self) -> Tuple[int, Union[Tuple[str, Condition, Condition], str]]:
        return (Condition.Binary, ("AND", p, q))

    c.doc = doc

    return c


def OrCond(p: Condition, q: Condition) -> Condition:
    def predicate(p: Condition, q: Condition, *args, **kwargs):
        b1 = p(*args, **kwargs)
        b2 = q(*args, **kwargs)
        return b1 or b2

    c = Condition()
    c.predicate = lambda *args, p=p, q=q: predicate(p, q, *args)

    def doc(self) -> Tuple[int, Union[Tuple[str, Condition, Condition], str]]:
        return (Condition.Binary, ("OR", p, q))

    c.doc = doc

    return c


class _ProtectedField(Generic[T]):
    def __init__(self, value: Optional[T] = None):
        self._value = value

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: T, field: ModelField):
        class _ValidationWrapper(BaseModel):
            value: field.type_._type

        *_, validation_error = validate_model(_ValidationWrapper, {"value": value})
        if validation_error:
            raise validation_error

        return value

    _value: Optional[T]


# Used to mangle dynamically created class names to avoid collisions during pydantic class name lookup.
NEW_PROTECTED_FIELD_CLASS_IDX: int = 0


def ProtectedField(
    field_title: str,
    typ: Type,
    condition: Condition,
    *,
    ignore_unauthorized_access: bool = False,
    safe_default: Optional[Any] = None,
    documented_condition: bool = True,
) -> Type:
    """
    Dynamically creates a new ProtectedField type that is used to annotate types in user models.
       Created class stores a Condition object and exposes `satisfied` method.
    :param field_title: Title of the field being annotated as it should appear in the schema.
    :param typ: Type of the field being annotated.
    :param condition: Condition object that should be called to authorize modifications to
        the value that field being annotated points to in a user model.
    :param ignore_unauthorized_access: Used by create_update_dict.
        If True, unauthorized accesses will not raise a UnauthorizedUpdateException
        but will safely ignore the unauthorized parts of the update.
        If True and the target_user (see create_update_dict doc) doesn't have a value for the field
        safe_default will be used to construct it.
    :param safe_default: A default value that can be used to construct the value that the
        field points to in a model. Must be specified iff ignore_unauthorized_access is True.
    :param documented_condition: Whether or not the condition for the protected field will
        be made available in the documentation. Set to False if the condition logic is sensitive.
    :rtype: Type used to annote model fields.
    """

    assert not condition is None, "Condition can not be None"
    assert ignore_unauthorized_access == (not safe_default is None)

    def constructor(self, *args, **kwargs):
        assert False, "This class is not supposed to be instantiated!"

    @classmethod
    def satisfied(cls, *args, **kwargs) -> Tuple[bool, Optional[Any]]:
        satisfied = cls._condition(*args, **kwargs)
        return (satisfied, cls._safe_default)

    class Config:
        title: str = f"Protected[{typ.__name__}]: {field_title}"

        @staticmethod
        def schema_extra(schema: dict[str, Any], model: type["Person"]) -> None:
            ...

    # Generate a decent documentation for the field.
    _doc_str = (
        f"Protected field of type <b>{typ.__name__}</b>.<br>"
        "Unauthorized accesses to this field will "
        f"<b>{'be quietly ignored' if  ignore_unauthorized_access else 'return with status code 403(FORBIDDEN)'}</b>."
    )
    if documented_condition:
        doc_str: str = f"{_doc_str}<br>Condition:<br>{get_condition_doc(condition)}"
    else:
        doc_str = _doc_str

    # creating class dynamically
    global NEW_PROTECTED_FIELD_CLASS_IDX
    NEW_PROTECTED_FIELD_CLASS_IDX += 1
    ProtectedFieldType = type(
        f"ProtectedFieldType_{NEW_PROTECTED_FIELD_CLASS_IDX}",
        (
            _ProtectedField,
            BaseModel,
        ),
        {
            "__init__": constructor,
            "__doc__": doc_str,
            "Config": Config,
            "_condition": condition,
            "_safe_default": safe_default,
            "_type": typ,
            "satisfied": satisfied,
        },
    )
    return ProtectedFieldType


def create_update_dict(
    user_schema: Type[BaseModel],
    user_update_schema: Type[BaseModel],
    actioning_user: Optional[Any],
    target_user: Optional[Any],
    update: Any,
) -> Dict[str, Any]:
    """
    This function returns a dictionary that will be used to create or update (used interchangably
        from here on), a model.
    Depending on the conditions set by the ProtectedFields of the class members,
        it might raise an exception if the actioning_user doesn't have rights to perform
        this particular update operation, or depending on the configuration it might ignore
        and safely delte unauthorized fields from the update.
    :param user_schema: type of the user model, actioning_user and target_user, if not None,
        must be of type `user_schema`
    :param user_schema: type of the update object, `update` must be of type `user_schema`
    :param actioning_user: User who is performing the update operation, for unauthorized accesses
        to the public endpoints it can be None.
    :param target_user: User who is being updated, when a new user is being created it can be None.
    :param udpate: Update object.
    :raises UnauthorizedUpdateException: if ignore_unauthorized_access is False
        for the protected field and the actioning_user modifies the value of a field it shouldn't.
    """

    assert isinstance(
        update, user_update_schema
    ), f"update ({type(update)} must be of type user_update_schema ({user_update_schema})"

    def assert_user_type(user: Optional[Any]):
        if user:
            assert isinstance(
                user, user_schema
            ), f"user ({type(user)}) must be of type user_schema ({user_schema})"

    assert_user_type(actioning_user)
    assert_user_type(target_user)

    for _, field in user_update_schema.__fields__.items():
        if not isinstance(field, ModelField):
            continue

        isprotected = issubclass(field.type_, _ProtectedField)
        if not isprotected:
            continue

        target_user_has_field = hasattr(target_user, field.name)
        update_has_field = hasattr(update, field.name)
        if not update_has_field:
            continue

        target_user_value = getattr(target_user, field.name, None)
        update_value = getattr(update, field.name, None)
        if not field.required and update_value is None:
            continue

        update_modifies_field = (
            update_has_field
            and (not target_user_has_field or target_user_value != update_value)
            and (
                update_value != field.default
                or (
                    field.name in user_schema.__fields__
                    and target_user_has_field
                    and target_user_value != user_schema.__fields__[field.name].default
                )
            )
        )
        if not update_modifies_field:
            continue

        has_modify_rights, safe_default = update_has_field and field.type_.satisfied(
            actioning_user, target_user, update
        )

        if not has_modify_rights:
            # safe_default != None if-and-only-if ignore_unauthorized_access=True
            if not safe_default is None:
                if target_user_has_field:
                    delattr(update, field.name)
                else:
                    setattr(update, field.name, safe_default)
            else:
                raise UnauthorizedUpdateException(field_name=field.name)

    return update.dict(exclude_unset=True, exclude={"id"})


# Shorthands for commonly used Conditions.
ActioningUserIsSuperUser = Requires(ActioningUser, "is_superuser", True)
IsSelfUpdate = Requires(ActioningUser, "id", "$(TargetUser).id")


class BaseUser(Generic[models.ID], BaseModel):
    """Base User model."""

    id: models.ID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class BaseUserCreate(BaseModel):
    email: EmailStr
    password: str
    is_active: Optional[
        ProtectedField(
            "Is Active",
            bool,
            ActioningUserIsSuperUser,
            ignore_unauthorized_access=True,
            safe_default=True,
        )
    ] = True
    is_superuser: Optional[
        ProtectedField(
            "Is Superuser",
            bool,
            ActioningUserIsSuperUser,
            ignore_unauthorized_access=True,
            safe_default=False,
        )
    ] = False
    is_verified: Optional[
        ProtectedField(
            "Is Verified",
            bool,
            ActioningUserIsSuperUser,
            ignore_unauthorized_access=True,
            safe_default=False,
        )
    ] = False


class BaseUserUpdate(BaseModel):
    password: Optional[
        ProtectedField(
            "Password",
            str,
            OrCond(ActioningUserIsSuperUser, IsSelfUpdate),
        )
    ]
    email: Optional[
        ProtectedField(
            "Email",
            EmailStr,
            OrCond(ActioningUserIsSuperUser, IsSelfUpdate),
        )
    ]
    is_active: Optional[
        ProtectedField(
            "Is Active",
            bool,
            ActioningUserIsSuperUser,
            ignore_unauthorized_access=True,
            safe_default=True,
        )
    ]
    is_superuser: Optional[
        ProtectedField(
            "Is Superuser",
            bool,
            ActioningUserIsSuperUser,
            ignore_unauthorized_access=True,
            safe_default=False,
        )
    ]
    is_verified: Optional[
        ProtectedField(
            "Is Verified",
            bool,
            ActioningUserIsSuperUser,
            ignore_unauthorized_access=True,
            safe_default=False,
        )
    ]


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)


class BaseOAuthAccount(Generic[models.ID], BaseModel):
    """Base OAuth account model."""

    id: models.ID
    oauth_name: str
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str

    class Config:
        orm_mode = True


class BaseOAuthAccountMixin(BaseModel):
    """Adds OAuth accounts list to a User model."""

    oauth_accounts: List[BaseOAuthAccount] = []
