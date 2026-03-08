from fastapi import Depends, HTTPException, status
from models import User, UserRole
from core.auth import get_current_user

_ROLES_ORDERED = [UserRole.member, UserRole.lab_admin, UserRole.company_admin, UserRole.super_admin]


def _rank(role: UserRole) -> int:
    return _ROLES_ORDERED.index(role)


def rank_of(role: UserRole) -> int:
    """Public helper for services that need to compare role ranks."""
    return _ROLES_ORDERED.index(role)


def _guard(min_role: UserRole):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if _rank(user.role) < _rank(min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {min_role.value} or above",
            )
        return user
    return dependency


require_member = _guard(UserRole.member)
require_lab_admin = _guard(UserRole.lab_admin)
require_company_admin = _guard(UserRole.company_admin)
require_super_admin = _guard(UserRole.super_admin)
