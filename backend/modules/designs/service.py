from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Design, User
from modules.designs.schemas import DesignCreate, DesignUpdate


def _get_lab_id(user: User) -> UUID:
    if not user.lab_id:
        raise HTTPException(403, "Lab membership required to access designs")
    return user.lab_id


async def list_designs(db: AsyncSession, current_user: User, skip: int, limit: int) -> tuple[list[Design], int]:
    lab_id = _get_lab_id(current_user)
    total = (
        await db.execute(select(func.count(Design.id)).where(Design.lab_id == lab_id))
    ).scalar()
    result = await db.execute(
        select(Design)
        .where(Design.lab_id == lab_id)
        .order_by(Design.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all(), total


async def get_design(db: AsyncSession, design_id: UUID, current_user: User) -> Design:
    lab_id = _get_lab_id(current_user)
    result = await db.execute(
        select(Design).where(Design.id == design_id, Design.lab_id == lab_id)
    )
    design = result.scalar_one_or_none()
    if not design:
        raise HTTPException(404, "Design not found")
    return design


async def create_design(db: AsyncSession, body: DesignCreate, current_user: User) -> Design:
    lab_id = _get_lab_id(current_user)
    design = Design(
        lab_id=lab_id,
        created_by=current_user.id,
        name=body.name,
        description=body.description,
        nodes=[],
        edges=[],
    )
    db.add(design)
    await db.commit()
    await db.refresh(design)
    return design


async def update_design(db: AsyncSession, design_id: UUID, body: DesignUpdate, current_user: User) -> Design:
    lab_id = _get_lab_id(current_user)
    result = await db.execute(
        select(Design).where(Design.id == design_id, Design.lab_id == lab_id)
    )
    design = result.scalar_one_or_none()
    if not design:
        raise HTTPException(404, "Design not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(design, field, value)
    design.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(design)
    return design


async def delete_design(db: AsyncSession, design_id: UUID, current_user: User) -> None:
    lab_id = _get_lab_id(current_user)
    result = await db.execute(
        select(Design).where(Design.id == design_id, Design.lab_id == lab_id)
    )
    design = result.scalar_one_or_none()
    if not design:
        raise HTTPException(404, "Design not found")
    await db.delete(design)
    await db.commit()
