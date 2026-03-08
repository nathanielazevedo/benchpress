from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import hash_password
from core.permissions import rank_of
from models import User, UserRole, Lab
from modules.users.schemas import UserCreate, UserUpdate


def _check_scope(current_user: User, target_lab_id: UUID | None) -> None:
    if current_user.role in (UserRole.super_admin, UserRole.company_admin):
        return
    if current_user.role == UserRole.lab_admin and target_lab_id != current_user.lab_id:
        raise HTTPException(403, "Lab admin can only manage users in their own lab")


def _check_role_assignment(current_user: User, requested_role: UserRole) -> None:
    if rank_of(requested_role) >= rank_of(current_user.role):
        raise HTTPException(403, f"Cannot assign role '{requested_role.value}' — must be below your own role")


async def list_users(db: AsyncSession, current_user: User, skip: int, limit: int) -> tuple[list[User], int]:
    filters = []
    if current_user.role == UserRole.lab_admin:
        filters.append(User.lab_id == current_user.lab_id)
    elif current_user.role == UserRole.company_admin:
        lab_ids = (
            await db.execute(select(Lab.id).where(Lab.company_id == current_user.lab.company_id))
        ).scalars().all()
        filters.append(User.lab_id.in_(lab_ids))

    total = (await db.execute(select(func.count(User.id)).where(*filters))).scalar()
    result = await db.execute(
        select(User).where(*filters).order_by(User.username).offset(skip).limit(limit)
    )
    return result.scalars().all(), total


async def get_user(db: AsyncSession, user_id: UUID, current_user: User) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    _check_scope(current_user, user.lab_id)
    return user


async def create_user(db: AsyncSession, body: UserCreate, current_user: User) -> User:
    _check_scope(current_user, body.lab_id)
    requested_role = UserRole(body.role)
    _check_role_assignment(current_user, requested_role)

    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Username already taken")

    if body.lab_id:
        lab = await db.get(Lab, body.lab_id)
        if not lab:
            raise HTTPException(404, "Lab not found")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        lab_id=body.lab_id,
        role=requested_role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: UUID, body: UserUpdate, current_user: User) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    _check_scope(current_user, user.lab_id)

    if body.username is not None:
        user.username = body.username
    if body.password is not None:
        user.password_hash = hash_password(body.password)
    if body.role is not None:
        requested_role = UserRole(body.role)
        _check_role_assignment(current_user, requested_role)
        user.role = requested_role

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: UUID, current_user: User) -> None:
    if str(user_id) == str(current_user.id):
        raise HTTPException(400, "Cannot delete your own account")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    _check_scope(current_user, user.lab_id)
    await db.delete(user)
    await db.commit()
