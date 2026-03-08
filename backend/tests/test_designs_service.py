"""Tests for modules/designs/service.py — lab scoping and CRUD."""
import uuid
from unittest.mock import MagicMock, AsyncMock
import pytest
from fastapi import HTTPException

from models import Design
from modules.designs.service import _get_lab_id, get_design, create_design
from modules.designs.schemas import DesignCreate
from tests.conftest import mock_db, mock_result


# ── _get_lab_id ───────────────────────────────────────────────────────────────

def test_get_lab_id_returns_lab_id_for_lab_member(member_user):
    lab_id = _get_lab_id(member_user)
    assert lab_id == member_user.lab_id


def test_get_lab_id_raises_for_super_admin(super_admin_user):
    with pytest.raises(HTTPException) as exc:
        _get_lab_id(super_admin_user)
    assert exc.value.status_code == 403
    assert "Lab membership" in exc.value.detail


# ── get_design ────────────────────────────────────────────────────────────────

async def test_get_design_returns_design_when_found(member_user):
    design = MagicMock(spec=Design)
    design.id = uuid.uuid4()
    design.lab_id = member_user.lab_id

    db = mock_db()
    db.execute = AsyncMock(return_value=mock_result(scalar=design))

    result = await get_design(db, design.id, member_user)
    assert result is design


async def test_get_design_raises_404_when_not_found(member_user):
    db = mock_db()
    db.execute = AsyncMock(return_value=mock_result(scalar=None))

    with pytest.raises(HTTPException) as exc:
        await get_design(db, uuid.uuid4(), member_user)
    assert exc.value.status_code == 404


# ── create_design ─────────────────────────────────────────────────────────────

async def test_create_design_sets_lab_and_creator(member_user):
    db = mock_db()

    created_design = MagicMock(spec=Design)
    created_design.id = uuid.uuid4()
    created_design.lab_id = member_user.lab_id
    created_design.created_by = member_user.id

    # db.refresh populates the object — simulate by making refresh set a return
    async def fake_refresh(obj):
        pass

    db.refresh = AsyncMock(side_effect=fake_refresh)

    body = DesignCreate(name="My Design")
    # Capture what was added to the db
    added = []
    db.add = MagicMock(side_effect=lambda obj: added.append(obj))

    await create_design(db, body, member_user)

    assert len(added) == 1
    new_design = added[0]
    assert new_design.lab_id == member_user.lab_id
    assert new_design.created_by == member_user.id
    assert new_design.name == "My Design"
    assert new_design.nodes == []
    assert new_design.edges == []
