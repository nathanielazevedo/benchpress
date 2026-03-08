"""Tests for core/permissions.py — role ranking and guard enforcement."""
import pytest
from fastapi import HTTPException

from core.permissions import rank_of
from models import UserRole


@pytest.mark.parametrize("role,expected", [
    (UserRole.member, 0),
    (UserRole.lab_admin, 1),
    (UserRole.company_admin, 2),
    (UserRole.super_admin, 3),
])
def test_rank_of_returns_correct_rank(role, expected):
    assert rank_of(role) == expected


def test_ranks_are_strictly_ordered():
    assert rank_of(UserRole.member) < rank_of(UserRole.lab_admin)
    assert rank_of(UserRole.lab_admin) < rank_of(UserRole.company_admin)
    assert rank_of(UserRole.company_admin) < rank_of(UserRole.super_admin)
