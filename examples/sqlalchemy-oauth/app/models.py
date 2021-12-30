from fastapi_users import models


class User(models.BaseUser, models.BaseOAuthAccountMixin):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass
