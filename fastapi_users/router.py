from fastapi import APIRouter

from .models import UserCreate, UserDB
from .password import get_password_hash

router = APIRouter()


@router.post('/register')
async def register(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    return UserDB(**user.dict(), hashed_password=hashed_password)
