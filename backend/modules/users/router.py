from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.permissions import require_lab_admin
from core.pagination import PageParams, Page
from models import User
from modules.users import service
from modules.users.schemas import UserCreate, UserUpdate, UserOut

router = APIRouter()


@router.get("", response_model=Page[UserOut], operation_id="listUsers")
async def list_users(
    page: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_lab_admin),
):
    items, total = await service.list_users(db, current_user, page.skip, page.limit)
    return Page(items=items, total=total, skip=page.skip, limit=page.limit)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED, operation_id="createUser")
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_lab_admin),
):
    return await service.create_user(db, body, current_user)


@router.get("/{user_id}", response_model=UserOut, operation_id="getUser")
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_lab_admin),
):
    return await service.get_user(db, user_id, current_user)


@router.put("/{user_id}", response_model=UserOut, operation_id="updateUser")
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_lab_admin),
):
    return await service.update_user(db, user_id, body, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteUser")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_lab_admin),
):
    await service.delete_user(db, user_id, current_user)
