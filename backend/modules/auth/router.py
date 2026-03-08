from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user
from models import User
from modules.auth import service
from modules.auth.schemas import LoginRequest, Token
from modules.users.schemas import UserMeOut

router = APIRouter()


@router.post("/login", response_model=Token, operation_id="loginUser")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await service.login(db, body)


@router.get("/me", response_model=UserMeOut, operation_id="getMe")
async def me(current_user: User = Depends(get_current_user)):
    return current_user
