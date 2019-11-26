from fastapi import FastAPI
from tortoise import Model
from tortoise.contrib.starlette import register_tortoise
from fastapi_users.db.tortoise import BaseUserModel, TortoiseUserDatabase

DATABASE_URL = "sqlite://./test.db"

class User(BaseUserModel, Model):
    pass

user_db = TortoiseUserDatabase(User)
app = FastAPI()

register_tortoise(app, modules={"models": ["path_to_your_package"]})

@app.get("/get")
async def get_user(id: str):
    # but also you can use standart User.get syntax
    return await user_db.get(id)
