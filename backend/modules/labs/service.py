from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Lab, Company, User, UserRole
from modules.labs.schemas import LabCreate, LabUpdate


async def list_labs(db: AsyncSession, current_user: User, skip: int, limit: int) -> tuple[list[Lab], int]:
    filters = []
    if current_user.role == UserRole.company_admin:
        filters.append(Lab.company_id == current_user.lab.company_id)

    total = (await db.execute(select(func.count(Lab.id)).where(*filters))).scalar()
    result = await db.execute(
        select(Lab).where(*filters).order_by(Lab.name).offset(skip).limit(limit)
    )
    return result.scalars().all(), total


async def get_lab(db: AsyncSession, lab_id: UUID, current_user: User) -> Lab:
    result = await db.execute(select(Lab).where(Lab.id == lab_id))
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(404, "Lab not found")
    if current_user.role == UserRole.company_admin and lab.company_id != current_user.lab.company_id:
        raise HTTPException(403, "Access denied")
    return lab


async def create_lab(db: AsyncSession, body: LabCreate, current_user: User) -> Lab:
    if current_user.role == UserRole.company_admin:
        if body.company_id != current_user.lab.company_id:
            raise HTTPException(403, "Cannot create labs in another company")

    company = await db.get(Company, body.company_id)
    if not company:
        raise HTTPException(404, "Company not found")

    lab = Lab(name=body.name, company_id=body.company_id)
    db.add(lab)
    await db.commit()
    await db.refresh(lab)
    return lab


async def update_lab(db: AsyncSession, lab_id: UUID, body: LabUpdate, current_user: User) -> Lab:
    result = await db.execute(select(Lab).where(Lab.id == lab_id))
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(404, "Lab not found")
    if current_user.role == UserRole.company_admin and lab.company_id != current_user.lab.company_id:
        raise HTTPException(403, "Access denied")
    lab.name = body.name
    await db.commit()
    await db.refresh(lab)
    return lab


async def delete_lab(db: AsyncSession, lab_id: UUID, current_user: User) -> None:
    result = await db.execute(select(Lab).where(Lab.id == lab_id))
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(404, "Lab not found")
    if current_user.role == UserRole.company_admin and lab.company_id != current_user.lab.company_id:
        raise HTTPException(403, "Access denied")
    await db.delete(lab)
    await db.commit()
