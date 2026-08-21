from fastapi_users import schemas


class UserCreate(schemas.BaseUserCreate):
    first_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None


class TestCreateUpdateDict:
    def test_create_update_dict_default_excludes_unset(self):
        user_create = UserCreate(email="king.arthur@camelot.bt", password="guinevere")

        assert user_create.create_update_dict() == {
            "email": "king.arthur@camelot.bt",
            "password": "guinevere",
        }

    def test_create_update_dict_include_defaults(self):
        user_create = UserCreate(email="king.arthur@camelot.bt", password="guinevere")

        assert user_create.create_update_dict(exclude_unset=False) == {
            "email": "king.arthur@camelot.bt",
            "password": "guinevere",
            "first_name": None,
        }

    def test_create_update_dict_exclude_superuser_fields(self):
        user_create = UserCreate(
            email="king.arthur@camelot.bt",
            password="guinevere",
            is_superuser=True,
            is_active=False,
        )

        assert user_create.create_update_dict() == {
            "email": "king.arthur@camelot.bt",
            "password": "guinevere",
        }

    def test_create_update_dict_superuser_default_excludes_unset(self):
        user_create = UserCreate(email="king.arthur@camelot.bt", password="guinevere")

        assert user_create.create_update_dict_superuser() == {
            "email": "king.arthur@camelot.bt",
            "password": "guinevere",
        }

    def test_create_update_dict_superuser_include_defaults(self):
        user_create = UserCreate(email="king.arthur@camelot.bt", password="guinevere")

        assert user_create.create_update_dict_superuser(exclude_unset=False) == {
            "email": "king.arthur@camelot.bt",
            "password": "guinevere",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "first_name": None,
        }

    def test_create_update_dict_superuser_include_superuser_fields(self):
        user_create = UserCreate(
            email="king.arthur@camelot.bt",
            password="guinevere",
            is_superuser=True,
            is_active=False,
        )

        assert user_create.create_update_dict_superuser() == {
            "email": "king.arthur@camelot.bt",
            "password": "guinevere",
            "is_superuser": True,
            "is_active": False,
        }


class TestUpdateCreateUpdateDict:
    def test_update_create_update_dict_default_excludes_unset(self):
        user_update = UserUpdate(password="holygrail")

        assert user_update.create_update_dict() == {"password": "holygrail"}

    def test_update_create_update_dict_include_defaults(self):
        user_update = UserUpdate(password="holygrail")

        assert user_update.create_update_dict(exclude_unset=False) == {
            "password": "holygrail",
            "email": None,
            "first_name": None,
        }

    def test_update_create_update_dict_superuser_default_excludes_unset(self):
        user_update = UserUpdate(password="holygrail", is_superuser=True)

        assert user_update.create_update_dict_superuser() == {
            "password": "holygrail",
            "is_superuser": True,
        }
