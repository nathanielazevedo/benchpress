from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.permissions import require_company_admin
from core.pagination import PageParams, Page
from models import User
from modules.labs import service
from modules.labs.schemas import LabCreate, LabUpdate, LabOut

router = APIRouter()


@router.get("", response_model=Page[LabOut], operation_id="listLabs")
async def list_labs(
    page: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    items, total = await service.list_labs(db, current_user, page.skip, page.limit)
    return Page(items=items, total=total, skip=page.skip, limit=page.limit)


@router.post("", response_model=LabOut, status_code=status.HTTP_201_CREATED, operation_id="createLab")
async def create_lab(
    body: LabCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return await service.create_lab(db, body, current_user)


@router.get("/{lab_id}", response_model=LabOut, operation_id="getLab")
async def get_lab(
    lab_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return await service.get_lab(db, lab_id, current_user)


@router.put("/{lab_id}", response_model=LabOut, operation_id="updateLab")
async def update_lab(
    lab_id: UUID,
    body: LabUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return await service.update_lab(db, lab_id, body, current_user)


@router.delete("/{lab_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteLab")
async def delete_lab(
    lab_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    await service.delete_lab(db, lab_id, current_user)
