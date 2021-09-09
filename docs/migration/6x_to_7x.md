# 6.x.x ➡️ 7.x.x

* The deprecated dependencies to retrieve current user have been removed. Use the `current_user` factory instead. [[Documentation](https://fastapi-users.github.io/fastapi-users/usage/current-user/)]
* When trying to authenticate a not verified user, a **status code 403** is raised instead of status code 401. Thanks @daanbeverdam 🎉 [[Documentation](https://fastapi-users.github.io/fastapi-users/usage/current-user/#current_user)]
* Your `UserUpdate` model shouldn't inherit from the base `User` class. If you have custom fields, you should repeat them in this model. [[Documentation](https://fastapi-users.github.io/fastapi-users/configuration/model/#define-your-models)]

---

* Database adapters now live in their [own repositories and packages](https://github.com/fastapi-users).
  * When upgrading to v7.0.0, the dependency for your database adapter should automatically be installed.
  * The `import` statements remain unchanged.
