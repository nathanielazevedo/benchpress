from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.permissions import require_member
from core.pagination import PageParams, Page
from models import User
from modules.designs import service
from modules.designs.schemas import DesignCreate, DesignUpdate, DesignOut, DesignSummary

router = APIRouter()


@router.get("", response_model=Page[DesignSummary], operation_id="listDesigns")
async def list_designs(
    page: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member),
):
    items, total = await service.list_designs(db, current_user, page.skip, page.limit)
    return Page(items=items, total=total, skip=page.skip, limit=page.limit)


@router.post("", response_model=DesignOut, status_code=status.HTTP_201_CREATED, operation_id="createDesign")
async def create_design(
    body: DesignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member),
):
    return await service.create_design(db, body, current_user)


@router.get("/{design_id}", response_model=DesignOut, operation_id="getDesign")
async def get_design(
    design_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member),
):
    return await service.get_design(db, design_id, current_user)


@router.put("/{design_id}", response_model=DesignOut, operation_id="updateDesign")
async def update_design(
    design_id: UUID,
    body: DesignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member),
):
    return await service.update_design(db, design_id, body, current_user)


@router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteDesign")
async def delete_design(
    design_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member),
):
    await service.delete_design(db, design_id, current_user)
