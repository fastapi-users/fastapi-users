from fastapi_users import models, schemas


class User(schemas.BaseUser, schemas.BaseOAuthAccountMixin):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UserDB(User, schemas.BaseUserDB):
    pass
