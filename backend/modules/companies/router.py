from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.permissions import require_super_admin
from core.pagination import PageParams, Page
from models import User
from modules.companies import service
from modules.companies.schemas import CompanyCreate, CompanyUpdate, CompanyOut, CompanyWithLabsOut

router = APIRouter()


@router.get("", response_model=Page[CompanyOut], operation_id="listCompanies")
async def list_companies(
    page: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    items, total = await service.list_companies(db, page.skip, page.limit)
    return Page(items=items, total=total, skip=page.skip, limit=page.limit)


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED, operation_id="createCompany")
async def create_company(
    body: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    return await service.create_company(db, body)


@router.get("/{company_id}", response_model=CompanyWithLabsOut, operation_id="getCompany")
async def get_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    return await service.get_company(db, company_id)


@router.put("/{company_id}", response_model=CompanyOut, operation_id="updateCompany")
async def update_company(
    company_id: UUID,
    body: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    return await service.update_company(db, company_id, body)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCompany")
async def delete_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    await service.delete_company(db, company_id)
