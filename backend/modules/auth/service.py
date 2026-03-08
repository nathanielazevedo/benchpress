from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.auth import verify_password, create_access_token
from models import User, Lab
from modules.auth.schemas import LoginRequest


async def login(db: AsyncSession, body: LoginRequest) -> dict:
    result = await db.execute(
        select(User)
        .options(selectinload(User.lab).selectinload(Lab.company))
        .where(User.username == body.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_access_token(user), "token_type": "bearer"}
