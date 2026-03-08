"""Tests for modules/users/service.py — role validation and scope checking."""
import uuid
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from models import User, UserRole
from modules.users.service import _check_scope, _check_role_assignment


# ── _check_scope ──────────────────────────────────────────────────────────────

def test_super_admin_can_manage_any_lab(super_admin_user):
    # Should not raise for any lab_id
    _check_scope(super_admin_user, uuid.uuid4())
    _check_scope(super_admin_user, None)


def test_company_admin_can_manage_any_lab(lab):
    user = MagicMock(spec=User)
    user.role = UserRole.company_admin
    _check_scope(user, uuid.uuid4())  # any lab — no raise


def test_lab_admin_can_only_manage_own_lab(lab_admin_user):
    # Same lab — OK
    _check_scope(lab_admin_user, lab_admin_user.lab_id)

    # Different lab — 403
    with pytest.raises(HTTPException) as exc:
        _check_scope(lab_admin_user, uuid.uuid4())
    assert exc.value.status_code == 403


# ── _check_role_assignment ────────────────────────────────────────────────────

def test_super_admin_can_assign_any_lower_role(super_admin_user):
    for role in [UserRole.member, UserRole.lab_admin, UserRole.company_admin]:
        _check_role_assignment(super_admin_user, role)  # no raise


def test_cannot_assign_equal_or_higher_role(lab_admin_user):
    # lab_admin trying to assign lab_admin (equal) — should raise
    with pytest.raises(HTTPException) as exc:
        _check_role_assignment(lab_admin_user, UserRole.lab_admin)
    assert exc.value.status_code == 403

    # lab_admin trying to assign company_admin (higher) — should raise
    with pytest.raises(HTTPException) as exc:
        _check_role_assignment(lab_admin_user, UserRole.company_admin)
    assert exc.value.status_code == 403


def test_member_cannot_assign_any_role(member_user):
    for role in [UserRole.member, UserRole.lab_admin, UserRole.company_admin, UserRole.super_admin]:
        with pytest.raises(HTTPException) as exc:
            _check_role_assignment(member_user, role)
        assert exc.value.status_code == 403
