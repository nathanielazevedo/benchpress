from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Company
from modules.companies.schemas import CompanyCreate, CompanyUpdate


async def list_companies(db: AsyncSession, skip: int, limit: int) -> tuple[list[Company], int]:
    total = (await db.execute(select(func.count(Company.id)))).scalar()
    result = await db.execute(select(Company).order_by(Company.name).offset(skip).limit(limit))
    return result.scalars().all(), total


async def get_company(db: AsyncSession, company_id: UUID) -> Company:
    result = await db.execute(
        select(Company).options(selectinload(Company.labs)).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    return company


async def create_company(db: AsyncSession, body: CompanyCreate) -> Company:
    existing = await db.execute(select(Company).where(Company.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Company name already exists")
    company = Company(name=body.name)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def update_company(db: AsyncSession, company_id: UUID, body: CompanyUpdate) -> Company:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    company.name = body.name
    await db.commit()
    await db.refresh(company)
    return company


async def delete_company(db: AsyncSession, company_id: UUID) -> None:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    await db.delete(company)
    await db.commit()
