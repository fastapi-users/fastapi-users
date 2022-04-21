# FastAPI Users

<p align="center">
  <img src="https://raw.githubusercontent.com/fastapi-users/fastapi-users/master/logo.svg?sanitize=true" alt="FastAPI Users">
</p>

<p align="center">
    <em>Ready-to-use and customizable users management for FastAPI </em>
</p>

[![build](https://github.com/fastapi-users/fastapi-users/workflows/Build/badge.svg)](https://github.com/fastapi-users/fastapi-users/actions)
[![codecov](https://codecov.io/gh/fastapi-users/fastapi-users/branch/master/graph/badge.svg)](https://codecov.io/gh/fastapi-users/fastapi-users)
[![PyPI version](https://badge.fury.io/py/fastapi-users.svg)](https://badge.fury.io/py/fastapi-users)
[![Downloads](https://pepy.tech/badge/fastapi-users)](https://pepy.tech/project/fastapi-users)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-54-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
<p align="center">
<a href="https://www.buymeacoffee.com/frankie567"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=frankie567&button_colour=FF5F5F&font_colour=ffffff&font_family=Arial&outline_colour=000000&coffee_colour=FFDD00"></a>
</p>

---

**Documentation**: <a href="https://fastapi-users.github.io/fastapi-users/" target="_blank">https://fastapi-users.github.io/fastapi-users/</a>

**Source Code**: <a href="https://github.com/fastapi-users/fastapi-users" target="_blank">https://github.com/fastapi-users/fastapi-users</a>

---

Add quickly a registration and authentication system to your [FastAPI](https://fastapi.tiangolo.com/) project. **FastAPI Users** is designed to be as customizable and adaptable as possible.

## Features

* [X] Extensible base user model
* [X] Ready-to-use register, login, reset password and verify e-mail routes
* [X] Ready-to-use social OAuth2 login flow
* [X] Dependency callables to inject current user in route
* [X] Pluggable password validation
* [X] Customizable database backend
    * [X] [SQLAlchemy ORM async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html) backend included
    * [X] MongoDB async backend included thanks to [mongodb/motor](https://github.com/mongodb/motor)
    * [X] [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/) backend included
    * [X] [ormar](https://collerek.github.io/ormar/) backend included
* [X] Multiple customizable authentication backends
    * [X] Transports: Authorization header, Cookie
    * [X] Strategies: JWT, Database, Redis
* [X] Full OpenAPI schema support, even with several authentication backends

## In a hurry? Discover Fief, the open-source authentication platform

<p align="center">
  <img src="https://raw.githubusercontent.com/fief-dev/.github/main/logos/logo-full-red.svg?sanitize=true" alt="Fief" width="256">
</p>

<img src="https://www.fief.dev/illustrations/guard-right.svg" alt="Fief" height="300" align="right">

**Implementing registration, login, social auth is hard and painful. We know it. With our highly secure and open-source users management platform, you can focus on your app while staying in control of your users data.**

* Based on **FastAPI Users**!
* **Open-source**: self-host it for free or use our hosted version
* **Bring your own database**: host your database anywhere, we'll take care of the rest
* **Pre-built login and registration pages**: clean and fast authentication so you don't have to do it yourself
* **Official Python client** with built-in **FastAPI integration**
* Integrate a simple face detection algorithm in a FastAPI backend
* Integrate common Python data science libraries in a web backend
* Deploy a performant and reliable web backend for a data science application

<p align="center">
    <a href="https://www.fief.dev"><img width="150px" src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+Cjxzdmcgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgdmlld0JveD0iMCAwIDIyMCA2MCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4bWw6c3BhY2U9InByZXNlcnZlIiB4bWxuczpzZXJpZj0iaHR0cDovL3d3dy5zZXJpZi5jb20vIiBzdHlsZT0iZmlsbC1ydWxlOmV2ZW5vZGQ7Y2xpcC1ydWxlOmV2ZW5vZGQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1taXRlcmxpbWl0OjI7Ij4KICAgIDxnIHRyYW5zZm9ybT0ibWF0cml4KDUuMDQ0MDgsMCwwLDIuNDcyMTYsLTYxLjkzMDQsLTE3Ljg1MDQpIj4KICAgICAgICA8cGF0aCBkPSJNNTUuODkzLDkuNzcyQzU1Ljg5Myw4LjM2NCA1NS4zMzMsNy4yMjEgNTQuNjQzLDcuMjIxTDEzLjUyOCw3LjIyMUMxMi44MzgsNy4yMjEgMTIuMjc4LDguMzY0IDEyLjI3OCw5Ljc3MkwxMi4yNzgsMjguOTM5QzEyLjI3OCwzMC4zNDggMTIuODM4LDMxLjQ5MSAxMy41MjgsMzEuNDkxTDU0LjY0MywzMS40OTFDNTUuMzMzLDMxLjQ5MSA1NS44OTMsMzAuMzQ4IDU1Ljg5MywyOC45MzlMNTUuODkzLDkuNzcyWiIgc3R5bGU9ImZpbGw6cmdiKDI0NCw2Myw5NCk7Ii8+CiAgICA8L2c+CiAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgxLDAsMCwxLC0xNC4wMjU2LC03LjY5MTI4KSI+CiAgICAgICAgPGcgdHJhbnNmb3JtPSJtYXRyaXgoMzAsMCwwLDMwLDI5LjM3NTQsNDguNjAwNCkiPgogICAgICAgICAgICA8cGF0aCBkPSJNMC4zNTksLTAuNzI3TDAuNDg5LC0wLjcyN0wwLjQ4OSwtMC4yMTZDMC40ODksLTAuMTY5IDAuNDc5LC0wLjEyOSAwLjQ2LC0wLjA5NUMwLjQ0LC0wLjA2MSAwLjQxMiwtMC4wMzUgMC4zNzcsLTAuMDE3QzAuMzQyLDAuMDAxIDAuMzAxLDAuMDEgMC4yNTUsMC4wMUMwLjIxMiwwLjAxIDAuMTc0LDAuMDAyIDAuMTQsLTAuMDEzQzAuMTA2LC0wLjAyOCAwLjA3OSwtMC4wNTEgMC4wNTksLTAuMDgxQzAuMDM5LC0wLjExMSAwLjAyOSwtMC4xNDggMC4wMjksLTAuMTkzTDAuMTYsLTAuMTkzQzAuMTYsLTAuMTc0IDAuMTY1LC0wLjE1NyAwLjE3MywtMC4xNDJDMC4xODIsLTAuMTI4IDAuMTkzLC0wLjExNyAwLjIwOCwtMC4xMUMwLjIyMywtMC4xMDIgMC4yNCwtMC4wOTggMC4yNiwtMC4wOThDMC4yODEsLTAuMDk4IDAuMjk5LC0wLjEwMyAwLjMxMywtMC4xMTJDMC4zMjgsLTAuMTIxIDAuMzM5LC0wLjEzNCAwLjM0NywtMC4xNTFDMC4zNTQsLTAuMTY5IDAuMzU4LC0wLjE5IDAuMzU5LC0wLjIxNkwwLjM1OSwtMC43MjdaIiBzdHlsZT0iZmlsbDp3aGl0ZTtmaWxsLXJ1bGU6bm9uemVybzsiLz4KICAgICAgICA8L2c+CiAgICAgICAgPGcgdHJhbnNmb3JtPSJtYXRyaXgoMzAsMCwwLDMwLDQ2LjE5NzIsNDguNjAwNCkiPgogICAgICAgICAgICA8cGF0aCBkPSJNMC4zMDQsMC4wMTFDMC4yNTEsMC4wMTEgMC4yMDUsLTAuMDAxIDAuMTY1LC0wLjAyNUMwLjEyNiwtMC4wNDggMC4wOTYsLTAuMDgxIDAuMDc1LC0wLjEyM0MwLjA1MywtMC4xNjUgMC4wNDMsLTAuMjE0IDAuMDQzLC0wLjI3MUMwLjA0MywtMC4zMjcgMC4wNTMsLTAuMzc2IDAuMDc1LC0wLjQxOUMwLjA5NiwtMC40NjEgMC4xMjYsLTAuNDk0IDAuMTY1LC0wLjUxN0MwLjIwNSwtMC41NDEgMC4yNTEsLTAuNTUzIDAuMzA0LC0wLjU1M0MwLjM1NywtMC41NTMgMC40MDMsLTAuNTQxIDAuNDQyLC0wLjUxN0MwLjQ4MiwtMC40OTQgMC41MTIsLTAuNDYxIDAuNTMzLC0wLjQxOUMwLjU1NSwtMC4zNzYgMC41NjUsLTAuMzI3IDAuNTY1LC0wLjI3MUMwLjU2NSwtMC4yMTQgMC41NTUsLTAuMTY1IDAuNTMzLC0wLjEyM0MwLjUxMiwtMC4wODEgMC40ODIsLTAuMDQ4IDAuNDQyLC0wLjAyNUMwLjQwMywtMC4wMDEgMC4zNTcsMC4wMTEgMC4zMDQsMC4wMTFaTTAuMzA1LC0wLjA5MkMwLjMzNCwtMC4wOTIgMC4zNTgsLTAuMSAwLjM3NywtMC4xMTZDMC4zOTcsLTAuMTMyIDAuNDExLC0wLjE1NCAwLjQyMSwtMC4xODFDMC40MywtMC4yMDggMC40MzUsLTAuMjM4IDAuNDM1LC0wLjI3MUMwLjQzNSwtMC4zMDQgMC40MywtMC4zMzUgMC40MjEsLTAuMzYyQzAuNDExLC0wLjM4OSAwLjM5NywtMC40MSAwLjM3NywtMC40MjZDMC4zNTgsLTAuNDQzIDAuMzM0LC0wLjQ1MSAwLjMwNSwtMC40NTFDMC4yNzUsLTAuNDUxIDAuMjUxLC0wLjQ0MyAwLjIzMSwtMC40MjZDMC4yMTEsLTAuNDEgMC4xOTcsLTAuMzg5IDAuMTg3LC0wLjM2MkMwLjE3OCwtMC4zMzUgMC4xNzMsLTAuMzA0IDAuMTczLC0wLjI3MUMwLjE3MywtMC4yMzggMC4xNzgsLTAuMjA4IDAuMTg3LC0wLjE4MUMwLjE5NywtMC4xNTQgMC4yMTEsLTAuMTMyIDAuMjMxLC0wLjExNkMwLjI1MSwtMC4xIDAuMjc1LC0wLjA5MiAwLjMwNSwtMC4wOTJaIiBzdHlsZT0iZmlsbDp3aGl0ZTtmaWxsLXJ1bGU6bm9uemVybzsiLz4KICAgICAgICA8L2c+CiAgICAgICAgPGcgdHJhbnNmb3JtPSJtYXRyaXgoMzAsMCwwLDMwLDY0LjQzNTgsNDguNjAwNCkiPgogICAgICAgICAgICA8cGF0aCBkPSJNMC4wNjYsLTBMMC4wNjYsLTAuNTQ1TDAuMTk1LC0wLjU0NUwwLjE5NSwtMEwwLjA2NiwtMFpNMC4xMzEsLTAuNjIzQzAuMTEsLTAuNjIzIDAuMDkzLC0wLjYzIDAuMDc4LC0wLjY0M0MwLjA2MywtMC42NTcgMC4wNTYsLTAuNjczIDAuMDU2LC0wLjY5MkMwLjA1NiwtMC43MTIgMC4wNjMsLTAuNzI4IDAuMDc4LC0wLjc0MkMwLjA5MywtMC43NTYgMC4xMSwtMC43NjIgMC4xMzEsLTAuNzYyQzAuMTUxLC0wLjc2MiAwLjE2OSwtMC43NTYgMC4xODMsLTAuNzQyQzAuMTk4LC0wLjcyOCAwLjIwNSwtMC43MTIgMC4yMDUsLTAuNjkyQzAuMjA1LC0wLjY3MyAwLjE5OCwtMC42NTcgMC4xODMsLTAuNjQzQzAuMTY5LC0wLjYzIDAuMTUxLC0wLjYyMyAwLjEzMSwtMC42MjNaIiBzdHlsZT0iZmlsbDp3aGl0ZTtmaWxsLXJ1bGU6bm9uemVybzsiLz4KICAgICAgICA8L2c+CiAgICAgICAgPGcgdHJhbnNmb3JtPSJtYXRyaXgoMzAsMCwwLDMwLDcyLjI1NTQsNDguNjAwNCkiPgogICAgICAgICAgICA8cGF0aCBkPSJNMC4xOTUsLTAuMzJMMC4xOTUsLTBMMC4wNjYsLTBMMC4wNjYsLTAuNTQ1TDAuMTg5LC0wLjU0NUwwLjE4OSwtMC40NTNMMC4xOTUsLTAuNDUzQzAuMjA4LC0wLjQ4MyAwLjIyOCwtMC41MDggMC4yNTYsLTAuNTI2QzAuMjgzLC0wLjU0NCAwLjMxNywtMC41NTMgMC4zNTgsLTAuNTUzQzAuMzk2LC0wLjU1MyAwLjQyOCwtMC41NDUgMC40NTYsLTAuNTI4QzAuNDg1LC0wLjUxMiAwLjUwNiwtMC40ODkgMC41MjIsLTAuNDU4QzAuNTM3LC0wLjQyOCAwLjU0NSwtMC4zOTEgMC41NDUsLTAuMzQ3TDAuNTQ1LC0wTDAuNDE2LC0wTDAuNDE2LC0wLjMyN0MwLjQxNiwtMC4zNjQgMC40MDcsLTAuMzkyIDAuMzg4LC0wLjQxM0MwLjM2OSwtMC40MzQgMC4zNDMsLTAuNDQ0IDAuMzEsLTAuNDQ0QzAuMjg4LC0wLjQ0NCAwLjI2OCwtMC40MzkgMC4yNSwtMC40MjlDMC4yMzMsLTAuNDE5IDAuMjE5LC0wLjQwNSAwLjIwOSwtMC4zODdDMC4yLC0wLjM2OCAwLjE5NSwtMC4zNDYgMC4xOTUsLTAuMzJaIiBzdHlsZT0iZmlsbDp3aGl0ZTtmaWxsLXJ1bGU6bm9uemVybzsiLz4KICAgICAgICA8L2c+CiAgICAgICAgPGcgdHJhbnNmb3JtPSJtYXRyaXgoMzAsMCwwLDMwLDk3Ljk5NCw0OC42MDA0KSI+CiAgICAgICAgICAgIDxwYXRoIGQ9Ik0wLjMzOCwtMC41NDVMMC4zMzgsLTAuNDQ2TDAuMDI1LC0wLjQ0NkwwLjAyNSwtMC41NDVMMC4zMzgsLTAuNTQ1Wk0wLjEwMiwtMC42NzZMMC4yMzEsLTAuNjc2TDAuMjMxLC0wLjE2NEMwLjIzMSwtMC4xNDcgMC4yMzMsLTAuMTM0IDAuMjM5LC0wLjEyNEMwLjI0NCwtMC4xMTUgMC4yNTEsLTAuMTA5IDAuMjYsLTAuMTA2QzAuMjY5LC0wLjEwMyAwLjI3OCwtMC4xMDEgMC4yODksLTAuMTAxQzAuMjk3LC0wLjEwMSAwLjMwNSwtMC4xMDEgMC4zMTEsLTAuMTAzQzAuMzE4LC0wLjEwNCAwLjMyMywtMC4xMDUgMC4zMjcsLTAuMTA2TDAuMzQ4LC0wLjAwNUMwLjM0MiwtMC4wMDMgMC4zMzIsLTAgMC4zMTksMC4wMDJDMC4zMDYsMC4wMDUgMC4yOTEsMC4wMDcgMC4yNzMsMC4wMDdDMC4yNDEsMC4wMDggMC4yMTIsMC4wMDMgMC4xODYsLTAuMDA3QzAuMTYsLTAuMDE4IDAuMTQsLTAuMDM1IDAuMTI0LC0wLjA1OEMwLjEwOSwtMC4wOCAwLjEwMiwtMC4xMDkgMC4xMDIsLTAuMTQzTDAuMTAyLC0wLjY3NloiIHN0eWxlPSJmaWxsOndoaXRlO2ZpbGwtcnVsZTpub256ZXJvOyIvPgogICAgICAgIDwvZz4KICAgICAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgzMCwwLDAsMzAsMTA5LjczNCw0OC42MDA0KSI+CiAgICAgICAgICAgIDxwYXRoIGQ9Ik0wLjE5NSwtMC4zMkwwLjE5NSwtMEwwLjA2NiwtMEwwLjA2NiwtMC43MjdMMC4xOTIsLTAuNzI3TDAuMTkyLC0wLjQ1M0wwLjE5OCwtMC40NTNDMC4yMTEsLTAuNDg0IDAuMjMxLC0wLjUwOCAwLjI1OCwtMC41MjZDMC4yODUsLTAuNTQ0IDAuMzE5LC0wLjU1MyAwLjM2LC0wLjU1M0MwLjM5OCwtMC41NTMgMC40MzEsLTAuNTQ1IDAuNDYsLTAuNTI5QzAuNDg4LC0wLjUxMyAwLjUxLC0wLjQ5IDAuNTI1LC0wLjQ1OUMwLjU0MSwtMC40MjkgMC41NDgsLTAuMzkxIDAuNTQ4LC0wLjM0N0wwLjU0OCwtMEwwLjQyLC0wTDAuNDIsLTAuMzI3QzAuNDIsLTAuMzY0IDAuNDEsLTAuMzkzIDAuMzkyLC0wLjQxM0MwLjM3MywtMC40MzQgMC4zNDYsLTAuNDQ0IDAuMzEzLC0wLjQ0NEMwLjI5LC0wLjQ0NCAwLjI2OSwtMC40MzkgMC4yNTIsLTAuNDI5QzAuMjM0LC0wLjQxOSAwLjIyLC0wLjQwNSAwLjIxLC0wLjM4N0MwLjIsLTAuMzY4IDAuMTk1LC0wLjM0NiAwLjE5NSwtMC4zMloiIHN0eWxlPSJmaWxsOndoaXRlO2ZpbGwtcnVsZTpub256ZXJvOyIvPgogICAgICAgIDwvZz4KICAgICAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgzMCwwLDAsMzAsMTI4LjEyMiw0OC42MDA0KSI+CiAgICAgICAgICAgIDxwYXRoIGQ9Ik0wLjMwOCwwLjAxMUMwLjI1MywwLjAxMSAwLjIwNiwtMC4wMDEgMC4xNjYsLTAuMDI0QzAuMTI2LC0wLjA0NiAwLjA5NiwtMC4wNzkgMC4wNzUsLTAuMTIxQzAuMDUzLC0wLjE2MyAwLjA0MywtMC4yMTIgMC4wNDMsLTAuMjdDMC4wNDMsLTAuMzI2IDAuMDUzLC0wLjM3NSAwLjA3NSwtMC40MTdDMC4wOTYsLTAuNDYgMC4xMjYsLTAuNDkzIDAuMTY1LC0wLjUxN0MwLjIwMywtMC41NDEgMC4yNDksLTAuNTUzIDAuMzAxLC0wLjU1M0MwLjMzNCwtMC41NTMgMC4zNjYsLTAuNTQ3IDAuMzk2LC0wLjUzNkMwLjQyNiwtMC41MjYgMC40NTMsLTAuNTA5IDAuNDc2LC0wLjQ4N0MwLjQ5OSwtMC40NjQgMC41MTcsLTAuNDM1IDAuNTMsLTAuNDAxQzAuNTQzLC0wLjM2NiAwLjU1LC0wLjMyNSAwLjU1LC0wLjI3N0wwLjU1LC0wLjIzOEwwLjEwMywtMC4yMzhMMC4xMDMsLTAuMzI0TDAuNDI3LC0wLjMyNEMwLjQyNywtMC4zNDkgMC40MjEsLTAuMzcxIDAuNDExLC0wLjM5QzAuNCwtMC40MDkgMC4zODYsLTAuNDI1IDAuMzY3LC0wLjQzNkMwLjM0OSwtMC40NDcgMC4zMjcsLTAuNDUyIDAuMzAzLC0wLjQ1MkMwLjI3NiwtMC40NTIgMC4yNTMsLTAuNDQ2IDAuMjMzLC0wLjQzM0MwLjIxMywtMC40MjEgMC4xOTgsLTAuNDA0IDAuMTg3LC0wLjM4NEMwLjE3NiwtMC4zNjMgMC4xNywtMC4zNDEgMC4xNywtMC4zMTZMMC4xNywtMC4yNDFDMC4xNywtMC4yMDkgMC4xNzYsLTAuMTgyIDAuMTg4LC0wLjE1OUMwLjE5OSwtMC4xMzcgMC4yMTUsLTAuMTE5IDAuMjM2LC0wLjEwN0MwLjI1NywtMC4wOTUgMC4yODEsLTAuMDg5IDAuMzA5LC0wLjA4OUMwLjMyOCwtMC4wODkgMC4zNDUsLTAuMDkyIDAuMzYsLTAuMDk3QzAuMzc1LC0wLjEwMyAwLjM4OCwtMC4xMTEgMC40LC0wLjEyMUMwLjQxMSwtMC4xMzIgMC40MTksLTAuMTQ0IDAuNDI1LC0wLjE2TDAuNTQ1LC0wLjE0NkMwLjUzNywtMC4xMTUgMC41MjMsLTAuMDg3IDAuNTAyLC0wLjA2M0MwLjQ4LC0wLjA0IDAuNDUzLC0wLjAyMiAwLjQyLC0wLjAwOUMwLjM4OCwwLjAwNCAwLjM1LDAuMDExIDAuMzA4LDAuMDExWiIgc3R5bGU9ImZpbGw6d2hpdGU7ZmlsbC1ydWxlOm5vbnplcm87Ii8+CiAgICAgICAgPC9nPgogICAgICAgIDxnIHRyYW5zZm9ybT0ibWF0cml4KDMwLDAsMCwzMCwxNTMuMzQ5LDQ4LjYwMDQpIj4KICAgICAgICAgICAgPHBhdGggZD0iTTAuMDcyLC0wTDAuMDcyLC0wLjcyN0wwLjIsLTAuNzI3TDAuMiwtMC40NTVMMC4yMDYsLTAuNDU1QzAuMjEyLC0wLjQ2OSAwLjIyMiwtMC40ODMgMC4yMzQsLTAuNDk4QzAuMjQ2LC0wLjUxMyAwLjI2MiwtMC41MjYgMC4yODMsLTAuNTM2QzAuMzAzLC0wLjU0NyAwLjMzLC0wLjU1MyAwLjM2MiwtMC41NTNDMC40MDQsLTAuNTUzIDAuNDQyLC0wLjU0MiAwLjQ3NiwtMC41MkMwLjUxLC0wLjQ5OSAwLjUzNywtMC40NjcgMC41NTcsLTAuNDI2QzAuNTc3LC0wLjM4NCAwLjU4NywtMC4zMzMgMC41ODcsLTAuMjcyQzAuNTg3LC0wLjIxMiAwLjU3NywtMC4xNjEgMC41NTcsLTAuMTE5QzAuNTM4LC0wLjA3NyAwLjUxMSwtMC4wNDUgMC40NzcsLTAuMDIzQzAuNDQzLC0wLjAwMSAwLjQwNSwwLjAxIDAuMzYyLDAuMDFDMC4zMzEsMC4wMSAwLjMwNSwwLjAwNCAwLjI4NCwtMC4wMDZDMC4yNjMsLTAuMDE2IDAuMjQ3LC0wLjAyOSAwLjIzNSwtMC4wNDRDMC4yMjIsLTAuMDU5IDAuMjEyLC0wLjA3MyAwLjIwNiwtMC4wODZMMC4xOTgsLTAuMDg2TDAuMTk4LC0wTDAuMDcyLC0wWk0wLjE5OCwtMC4yNzNDMC4xOTgsLTAuMjM3IDAuMjAzLC0wLjIwNyAwLjIxMywtMC4xOEMwLjIyMywtMC4xNTQgMC4yMzgsLTAuMTMzIDAuMjU3LC0wLjExOEMwLjI3NiwtMC4xMDMgMC4yOTksLTAuMDk2IDAuMzI2LC0wLjA5NkMwLjM1NCwtMC4wOTYgMC4zNzgsLTAuMTA0IDAuMzk3LC0wLjExOUMwLjQxNywtMC4xMzQgMC40MzEsLTAuMTU1IDAuNDQxLC0wLjE4MkMwLjQ1MSwtMC4yMDggMC40NTYsLTAuMjM5IDAuNDU2LC0wLjI3M0MwLjQ1NiwtMC4zMDcgMC40NTEsLTAuMzM3IDAuNDQxLC0wLjM2M0MwLjQzMSwtMC4zODkgMC40MTcsLTAuNDEgMC4zOTgsLTAuNDI1QzAuMzc5LC0wLjQ0IDAuMzU1LC0wLjQ0NyAwLjMyNiwtMC40NDdDMC4yOTksLTAuNDQ3IDAuMjc1LC0wLjQ0IDAuMjU2LC0wLjQyNUMwLjIzNywtMC40MTEgMC4yMjIsLTAuMzkxIDAuMjEzLC0wLjM2NUMwLjIwMywtMC4zMzkgMC4xOTgsLTAuMzA4IDAuMTk4LC0wLjI3M1oiIHN0eWxlPSJmaWxsOndoaXRlO2ZpbGwtcnVsZTpub256ZXJvOyIvPgogICAgICAgIDwvZz4KICAgICAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgzMCwwLDAsMzAsMTcyLjI1OSw0OC42MDA0KSI+CiAgICAgICAgICAgIDxwYXRoIGQ9Ik0wLjMwOCwwLjAxMUMwLjI1MywwLjAxMSAwLjIwNiwtMC4wMDEgMC4xNjYsLTAuMDI0QzAuMTI2LC0wLjA0NiAwLjA5NiwtMC4wNzkgMC4wNzUsLTAuMTIxQzAuMDUzLC0wLjE2MyAwLjA0MywtMC4yMTIgMC4wNDMsLTAuMjdDMC4wNDMsLTAuMzI2IDAuMDUzLC0wLjM3NSAwLjA3NSwtMC40MTdDMC4wOTYsLTAuNDYgMC4xMjYsLTAuNDkzIDAuMTY1LC0wLjUxN0MwLjIwMywtMC41NDEgMC4yNDksLTAuNTUzIDAuMzAxLC0wLjU1M0MwLjMzNCwtMC41NTMgMC4zNjYsLTAuNTQ3IDAuMzk2LC0wLjUzNkMwLjQyNiwtMC41MjYgMC40NTMsLTAuNTA5IDAuNDc2LC0wLjQ4N0MwLjQ5OSwtMC40NjQgMC41MTcsLTAuNDM1IDAuNTMsLTAuNDAxQzAuNTQzLC0wLjM2NiAwLjU1LC0wLjMyNSAwLjU1LC0wLjI3N0wwLjU1LC0wLjIzOEwwLjEwMywtMC4yMzhMMC4xMDMsLTAuMzI0TDAuNDI3LC0wLjMyNEMwLjQyNywtMC4zNDkgMC40MjEsLTAuMzcxIDAuNDExLC0wLjM5QzAuNCwtMC40MDkgMC4zODYsLTAuNDI1IDAuMzY3LC0wLjQzNkMwLjM0OSwtMC40NDcgMC4zMjcsLTAuNDUyIDAuMzAzLC0wLjQ1MkMwLjI3NiwtMC40NTIgMC4yNTMsLTAuNDQ2IDAuMjMzLC0wLjQzM0MwLjIxMywtMC40MjEgMC4xOTgsLTAuNDA0IDAuMTg3LC0wLjM4NEMwLjE3NiwtMC4zNjMgMC4xNywtMC4zNDEgMC4xNywtMC4zMTZMMC4xNywtMC4yNDFDMC4xNywtMC4yMDkgMC4xNzYsLTAuMTgyIDAuMTg4LC0wLjE1OUMwLjE5OSwtMC4xMzcgMC4yMTUsLTAuMTE5IDAuMjM2LC0wLjEwN0MwLjI1NywtMC4wOTUgMC4yODEsLTAuMDg5IDAuMzA5LC0wLjA4OUMwLjMyOCwtMC4wODkgMC4zNDUsLTAuMDkyIDAuMzYsLTAuMDk3QzAuMzc1LC0wLjEwMyAwLjM4OCwtMC4xMTEgMC40LC0wLjEyMUMwLjQxMSwtMC4xMzIgMC40MTksLTAuMTQ0IDAuNDI1LC0wLjE2TDAuNTQ1LC0wLjE0NkMwLjUzNywtMC4xMTUgMC41MjMsLTAuMDg3IDAuNTAyLC0wLjA2M0MwLjQ4LC0wLjA0IDAuNDUzLC0wLjAyMiAwLjQyLC0wLjAwOUMwLjM4OCwwLjAwNCAwLjM1LDAuMDExIDAuMzA4LDAuMDExWiIgc3R5bGU9ImZpbGw6d2hpdGU7ZmlsbC1ydWxlOm5vbnplcm87Ii8+CiAgICAgICAgPC9nPgogICAgICAgIDxnIHRyYW5zZm9ybT0ibWF0cml4KDMwLDAsMCwzMCwxOTAuMDM5LDQ4LjYwMDQpIj4KICAgICAgICAgICAgPHBhdGggZD0iTTAuMzM4LC0wLjU0NUwwLjMzOCwtMC40NDZMMC4wMjUsLTAuNDQ2TDAuMDI1LC0wLjU0NUwwLjMzOCwtMC41NDVaTTAuMTAyLC0wLjY3NkwwLjIzMSwtMC42NzZMMC4yMzEsLTAuMTY0QzAuMjMxLC0wLjE0NyAwLjIzMywtMC4xMzQgMC4yMzksLTAuMTI0QzAuMjQ0LC0wLjExNSAwLjI1MSwtMC4xMDkgMC4yNiwtMC4xMDZDMC4yNjksLTAuMTAzIDAuMjc4LC0wLjEwMSAwLjI4OSwtMC4xMDFDMC4yOTcsLTAuMTAxIDAuMzA1LC0wLjEwMSAwLjMxMSwtMC4xMDNDMC4zMTgsLTAuMTA0IDAuMzIzLC0wLjEwNSAwLjMyNywtMC4xMDZMMC4zNDgsLTAuMDA1QzAuMzQyLC0wLjAwMyAwLjMzMiwtMCAwLjMxOSwwLjAwMkMwLjMwNiwwLjAwNSAwLjI5MSwwLjAwNyAwLjI3MywwLjAwN0MwLjI0MSwwLjAwOCAwLjIxMiwwLjAwMyAwLjE4NiwtMC4wMDdDMC4xNiwtMC4wMTggMC4xNCwtMC4wMzUgMC4xMjQsLTAuMDU4QzAuMTA5LC0wLjA4IDAuMTAyLC0wLjEwOSAwLjEwMiwtMC4xNDNMMC4xMDIsLTAuNjc2WiIgc3R5bGU9ImZpbGw6d2hpdGU7ZmlsbC1ydWxlOm5vbnplcm87Ii8+CiAgICAgICAgPC9nPgogICAgICAgIDxnIHRyYW5zZm9ybT0ibWF0cml4KDMwLDAsMCwzMCwyMDEuNDM5LDQ4LjYwMDQpIj4KICAgICAgICAgICAgPHBhdGggZD0iTTAuMjIzLDAuMDExQzAuMTg4LDAuMDExIDAuMTU3LDAuMDA1IDAuMTMsLTAuMDA4QzAuMTAyLC0wLjAyIDAuMDgsLTAuMDM4IDAuMDY0LC0wLjA2M0MwLjA0OCwtMC4wODcgMC4wNCwtMC4xMTcgMC4wNCwtMC4xNTNDMC4wNCwtMC4xODQgMC4wNDYsLTAuMjA5IDAuMDU4LC0wLjIyOUMwLjA2OSwtMC4yNSAwLjA4NCwtMC4yNjYgMC4xMDQsLTAuMjc4QzAuMTI0LC0wLjI5IDAuMTQ2LC0wLjI5OSAwLjE3MSwtMC4zMDVDMC4xOTUsLTAuMzExIDAuMjIxLC0wLjMxNiAwLjI0OCwtMC4zMTlDMC4yNzksLTAuMzIyIDAuMzA1LC0wLjMyNSAwLjMyNSwtMC4zMjhDMC4zNDUsLTAuMzMxIDAuMzYsLTAuMzM1IDAuMzY5LC0wLjM0MUMwLjM3OCwtMC4zNDcgMC4zODIsLTAuMzU2IDAuMzgyLC0wLjM2OEwwLjM4MiwtMC4zN0MwLjM4MiwtMC4zOTcgMC4zNzUsLTAuNDE3IDAuMzU5LC0wLjQzMkMwLjM0MywtMC40NDcgMC4zMiwtMC40NTQgMC4yOSwtMC40NTRDMC4yNTksLTAuNDU0IDAuMjM0LC0wLjQ0NyAwLjIxNSwtMC40MzRDMC4xOTcsLTAuNDIgMC4xODUsLTAuNDA0IDAuMTc4LC0wLjM4NUwwLjA1OCwtMC40MDJDMC4wNjgsLTAuNDM1IDAuMDgzLC0wLjQ2MyAwLjEwNSwtMC40ODVDMC4xMjcsLTAuNTA4IDAuMTU0LC0wLjUyNCAwLjE4NSwtMC41MzZDMC4yMTcsLTAuNTQ3IDAuMjUxLC0wLjU1MyAwLjI4OSwtMC41NTNDMC4zMTYsLTAuNTUzIDAuMzQyLC0wLjU0OSAwLjM2OCwtMC41NDNDMC4zOTQsLTAuNTM3IDAuNDE4LC0wLjUyNyAwLjQzOSwtMC41MTNDMC40NjEsLTAuNDk5IDAuNDc4LC0wLjQ4IDAuNDkxLC0wLjQ1NkMwLjUwNCwtMC40MzEgMC41MTEsLTAuNDAxIDAuNTExLC0wLjM2NUwwLjUxMSwtMEwwLjM4NywtMEwwLjM4NywtMC4wNzVMMC4zODMsLTAuMDc1QzAuMzc1LC0wLjA2IDAuMzY0LC0wLjA0NiAwLjM1LC0wLjAzMkMwLjMzNiwtMC4wMTkgMC4zMTksLTAuMDA5IDAuMjk3LC0wLjAwMUMwLjI3NiwwLjAwNyAwLjI1MSwwLjAxMSAwLjIyMywwLjAxMVpNMC4yNTYsLTAuMDgzQzAuMjgyLC0wLjA4MyAwLjMwNSwtMC4wODkgMC4zMjQsLTAuMDk5QzAuMzQyLC0wLjEwOSAwLjM1NywtMC4xMjMgMC4zNjcsLTAuMTRDMC4zNzgsLTAuMTU3IDAuMzgzLC0wLjE3NiAwLjM4MywtMC4xOTZMMC4zODMsLTAuMjZDMC4zNzksLTAuMjU3IDAuMzcyLC0wLjI1NCAwLjM2MiwtMC4yNTFDMC4zNTMsLTAuMjQ4IDAuMzQyLC0wLjI0NSAwLjMzLC0wLjI0M0MwLjMxOCwtMC4yNDEgMC4zMDcsLTAuMjM5IDAuMjk1LC0wLjIzOEMwLjI4MywtMC4yMzYgMC4yNzMsLTAuMjM0IDAuMjY1LC0wLjIzM0MwLjI0NiwtMC4yMzEgMC4yMjksLTAuMjI2IDAuMjEzLC0wLjIyMUMwLjE5OCwtMC4yMTUgMC4xODYsLTAuMjA2IDAuMTc4LC0wLjE5NkMwLjE2OSwtMC4xODUgMC4xNjQsLTAuMTcyIDAuMTY0LC0wLjE1NUMwLjE2NCwtMC4xMzIgMC4xNzMsLTAuMTE0IDAuMTksLTAuMTAyQzAuMjA4LC0wLjA4OSAwLjIzLC0wLjA4MyAwLjI1NiwtMC4wODNaIiBzdHlsZT0iZmlsbDp3aGl0ZTtmaWxsLXJ1bGU6bm9uemVybzsiLz4KICAgICAgICA8L2c+CiAgICA8L2c+Cjwvc3ZnPgo=" /></a>
</p>
<p align="center">It's free!</p>

## Contributors and sponsors ✨☕️

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://francoisvoron.com"><img src="https://avatars.githubusercontent.com/u/1144727?v=4?s=100" width="100px;" alt=""/><br /><sub><b>François Voron</b></sub></a><br /><a href="#maintenance-frankie567" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/paolodina"><img src="https://avatars.githubusercontent.com/u/1157401?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Paolo Dina</b></sub></a><br /><a href="#financial-paolodina" title="Financial">💵</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=paolodina" title="Code">💻</a></td>
    <td align="center"><a href="https://freelancehunt.com/freelancer/slado122.html"><img src="https://avatars.githubusercontent.com/u/46085159?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Dmytro Ohorodnik</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aslado122" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://matthewscholefield.github.io"><img src="https://avatars.githubusercontent.com/u/5875019?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Matthew D. Scholefield</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AMatthewScholefield" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/roywes"><img src="https://avatars.githubusercontent.com/u/3861579?v=4?s=100" width="100px;" alt=""/><br /><sub><b>roywes</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aroywes" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=roywes" title="Code">💻</a></td>
    <td align="center"><a href="https://devwriters.com"><img src="https://avatars.githubusercontent.com/u/10217535?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Satwik Kansal</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=satwikkansal" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/eddsalkield"><img src="https://avatars.githubusercontent.com/u/30939717?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Edd Salkield</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=eddsalkield" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=eddsalkield" title="Documentation">📖</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/mark-todd"><img src="https://avatars.githubusercontent.com/u/60781787?v=4?s=100" width="100px;" alt=""/><br /><sub><b>mark-todd</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=mark-todd" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=mark-todd" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/lill74"><img src="https://avatars.githubusercontent.com/u/12353597?v=4?s=100" width="100px;" alt=""/><br /><sub><b>lill74</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Alill74" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=lill74" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=lill74" title="Documentation">📖</a></td>
    <td align="center"><a href="https://yacht.sh"><img src="https://avatars.githubusercontent.com/u/66331933?v=4?s=100" width="100px;" alt=""/><br /><sub><b>SelfhostedPro</b></sub></a><br /><a href="#security-SelfhostedPro" title="Security">🛡️</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=SelfhostedPro" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/oskar-gmerek"><img src="https://avatars.githubusercontent.com/u/53402105?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Oskar Gmerek</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=oskar-gmerek" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/mcolladoio"><img src="https://avatars.githubusercontent.com/u/61695048?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Martin Collado</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Amcolladoio" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=mcolladoio" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/nullhack"><img src="https://avatars.githubusercontent.com/u/11466701?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Eric Lopes</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=nullhack" title="Documentation">📖</a> <a href="#security-nullhack" title="Security">🛡️</a></td>
    <td align="center"><a href="https://github.com/rnd42"><img src="https://avatars.githubusercontent.com/u/618839?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Beau Breon</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=rnd42" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/niazangels"><img src="https://avatars.githubusercontent.com/u/2761491?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Niyas Mohammed</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=niazangels" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/prostomarkeloff"><img src="https://avatars.githubusercontent.com/u/28061158?v=4?s=100" width="100px;" alt=""/><br /><sub><b>prostomarkeloff</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=prostomarkeloff" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=prostomarkeloff" title="Code">💻</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/mariusmezerette/"><img src="https://avatars.githubusercontent.com/u/952685?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Marius Mézerette</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AMariusMez" title="Bug reports">🐛</a> <a href="#ideas-MariusMez" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/grigi"><img src="https://avatars.githubusercontent.com/u/1309160?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nickolas Grigoriadis</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Agrigi" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://opendatacoder.me"><img src="https://avatars.githubusercontent.com/u/7386680?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Open Data Coder</b></sub></a><br /><a href="#ideas-p3t3r67x0" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://www.dralshehri.com/"><img src="https://avatars.githubusercontent.com/u/542855?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Mohammed Alshehri</b></sub></a><br /><a href="#ideas-dralshehri" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/lefnire/"><img src="https://avatars.githubusercontent.com/u/195202?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Tyler Renelle</b></sub></a><br /><a href="#ideas-lefnire" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/collerek"><img src="https://avatars.githubusercontent.com/u/16324238?v=4?s=100" width="100px;" alt=""/><br /><sub><b>collerek</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=collerek" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rbracco"><img src="https://avatars.githubusercontent.com/u/47190785?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Robert Bracco</b></sub></a><br /><a href="#financial-rbracco" title="Financial">💵</a></td>
    <td align="center"><a href="https://herrmann.tech"><img src="https://avatars.githubusercontent.com/u/1058414?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Augusto Herrmann</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=augusto-herrmann" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/Smithybrewer"><img src="https://avatars.githubusercontent.com/u/57669591?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Smithybrewer</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3ASmithybrewer" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/silllli"><img src="https://avatars.githubusercontent.com/u/9334305?v=4?s=100" width="100px;" alt=""/><br /><sub><b>silllli</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=silllli" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/alexferrari88"><img src="https://avatars.githubusercontent.com/u/49028826?v=4?s=100" width="100px;" alt=""/><br /><sub><b>alexferrari88</b></sub></a><br /><a href="#financial-alexferrari88" title="Financial">💵</a></td>
    <td align="center"><a href="https://github.com/sandalwoodbox"><img src="https://avatars.githubusercontent.com/u/80227316?v=4?s=100" width="100px;" alt=""/><br /><sub><b>sandalwoodbox</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Asandalwoodbox" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/vladhoi"><img src="https://avatars.githubusercontent.com/u/33840957?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vlad Hoi</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=vladhoi" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/jnu"><img src="https://avatars.githubusercontent.com/u/1069899?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Joe Nudell</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ajnu" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/cosmosquark"><img src="https://avatars.githubusercontent.com/u/1540682?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ben</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=cosmosquark" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/BoYanZh"><img src="https://avatars.githubusercontent.com/u/32470225?v=4?s=100" width="100px;" alt=""/><br /><sub><b>BoYanZh</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=BoYanZh" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/davidbrochart"><img src="https://avatars.githubusercontent.com/u/4711805?v=4?s=100" width="100px;" alt=""/><br /><sub><b>David Brochart</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=davidbrochart" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=davidbrochart" title="Code">💻</a></td>
    <td align="center"><a href="https://www.daanbeverdam.com"><img src="https://avatars.githubusercontent.com/u/13944585?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Daan Beverdam</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=daanbeverdam" title="Code">💻</a></td>
    <td align="center"><a href="http://sralab.com"><img src="https://avatars.githubusercontent.com/u/1815?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Stéphane Raimbault</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=stephane" title="Tests">⚠️</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Astephane" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/sondrelg"><img src="https://avatars.githubusercontent.com/u/25310870?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Sondre Lillebø Gundersen</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=sondrelg" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/maximka1221"><img src="https://avatars.githubusercontent.com/u/1503245?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Maxim</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=maximka1221" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Amaximka1221" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/scottdavort"><img src="https://avatars.githubusercontent.com/u/58272461?v=4?s=100" width="100px;" alt=""/><br /><sub><b>scottdavort</b></sub></a><br /><a href="#financial-scottdavort" title="Financial">💵</a></td>
    <td align="center"><a href="https://github.com/jdukewich"><img src="https://avatars.githubusercontent.com/u/37190801?v=4?s=100" width="100px;" alt=""/><br /><sub><b>John Dukewich</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=jdukewich" title="Documentation">📖</a></td>
    <td align="center"><a href="http://yezz.me"><img src="https://avatars.githubusercontent.com/u/52716203?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Yasser Tahiri</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=yezz123" title="Code">💻</a></td>
    <td align="center"><a href="https://www.brandongoding.tech"><img src="https://avatars.githubusercontent.com/u/17888319?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Brandon H. Goding</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=BrandonGoding" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/PovilasKud"><img src="https://avatars.githubusercontent.com/u/7852173?v=4?s=100" width="100px;" alt=""/><br /><sub><b>PovilasK</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=PovilasKud" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="http://justobjects.nl"><img src="https://avatars.githubusercontent.com/u/582630?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Just van den Broecke</b></sub></a><br /><a href="#financial-justb4" title="Financial">💵</a></td>
    <td align="center"><a href="https://github.com/jakemanger"><img src="https://avatars.githubusercontent.com/u/52495554?v=4?s=100" width="100px;" alt=""/><br /><sub><b>jakemanger</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ajakemanger" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=jakemanger" title="Code">💻</a></td>
    <td align="center"><a href="https://bandism.net/"><img src="https://avatars.githubusercontent.com/u/22633385?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ikko Ashimine</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=eltociear" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/matyasrichter"><img src="https://avatars.githubusercontent.com/u/20258539?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Matyáš Richter</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=matyasrichter" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Hazedd"><img src="https://avatars.githubusercontent.com/u/20663495?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Hazedd</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AHazedd" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=Hazedd" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/luisroel91"><img src="https://avatars.githubusercontent.com/u/44761184?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Luis Roel</b></sub></a><br /><a href="#financial-luisroel91" title="Financial">💵</a></td>
    <td align="center"><a href="https://ae-mc.ru"><img src="https://avatars.githubusercontent.com/u/43097289?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Alexandr Makurin</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=Ae-Mc" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AAe-Mc" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="http://www.retoflow.de"><img src="https://avatars.githubusercontent.com/u/23637821?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Leon Thurner</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=lthurner" title="Documentation">📖</a></td>
    <td align="center"><a href="http://meka.rs"><img src="https://avatars.githubusercontent.com/u/610855?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Goran Mekić</b></sub></a><br /><a href="#platform-mekanix" title="Packaging/porting to new platform">📦</a></td>
    <td align="center"><a href="https://gaganpreet.in/"><img src="https://avatars.githubusercontent.com/u/815873?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Gaganpreet</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=gaganpreet" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/jtv8"><img src="https://avatars.githubusercontent.com/u/29302451?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Joe Taylor</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=jtv8" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/ricfri"><img src="https://avatars.githubusercontent.com/u/21967765?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Richard Friberg</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aricfri" title="Bug reports">🐛</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Development

### Setup environment

You should create a virtual environment and activate it:

```bash
python -m venv venv/
```

```bash
source venv/bin/activate
```

And then install the development dependencies:

```bash
make install
```

### Run unit tests

You can run all the tests with:

```bash
make test
```

Alternatively, you can run `pytest` yourself.

```bash
pytest
```

There are quite a few unit tests, so you might run into ulimit issues where there are too many open file descriptors. You may be able to set a new, higher limit temporarily with:

```bash
ulimit -n 2048
```

### Format the code

Execute the following command to apply `isort` and `black` formatting:

```bash
make format
```

## License

This project is licensed under the terms of the MIT license.
