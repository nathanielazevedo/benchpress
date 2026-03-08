"""
Shared fixtures for all backend tests.

DB strategy: we never connect to a real database. Instead each test configures
an AsyncMock session and installs it via FastAPI's dependency_overrides.
The mock_result() helper makes it easy to fake SQLAlchemy result objects.
"""
import os
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
from passlib.context import CryptContext
from httpx import AsyncClient, ASGITransport

# Set required env vars before importing any app module so pydantic-settings
# doesn't raise a validation error.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-32-chars-minimum!!")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from main import app  # noqa: E402 — must come after env vars
from core.database import get_db  # noqa: E402
import core.auth as _core_auth  # noqa: E402
from core.auth import get_current_user  # noqa: E402
from models import User, UserRole, Lab, Company  # noqa: E402

# Swap bcrypt (incompatible with bcrypt>=4.x in some envs) for sha256_crypt in tests.
_core_auth.pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


# ── DB mock helpers ───────────────────────────────────────────────────────────

def mock_result(scalar=None, rows=None):
    """Return a fake SQLAlchemy execute() result."""
    r = MagicMock()
    r.scalar_one_or_none.return_value = scalar
    r.scalar.return_value = scalar
    r.scalars.return_value.all.return_value = rows if rows is not None else []
    return r


def mock_db(side_effects=None):
    """
    Return an AsyncMock AsyncSession.

    Pass side_effects as a list to simulate multiple execute() calls in order,
    or leave None to configure db.execute.return_value per test.
    """
    db = AsyncMock()
    db.get = AsyncMock(return_value=None)
    db.add = MagicMock()
    db.delete = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    if side_effects is not None:
        db.execute = AsyncMock(side_effect=side_effects)
    return db


# ── User fixtures ─────────────────────────────────────────────────────────────

def _make_company() -> Company:
    c = MagicMock(spec=Company)
    c.id = uuid.uuid4()
    c.name = "Test Company"
    c.created_at = datetime.utcnow()
    return c


def _make_lab(company: Company) -> Lab:
    lab = MagicMock(spec=Lab)
    lab.id = uuid.uuid4()
    lab.name = "Test Lab"
    lab.company_id = company.id
    lab.company = company
    lab.created_at = datetime.utcnow()
    return lab


@pytest.fixture
def company():
    return _make_company()


@pytest.fixture
def lab(company):
    return _make_lab(company)


@pytest.fixture
def super_admin_user():
    u = MagicMock(spec=User)
    u.id = uuid.uuid4()
    u.username = "admin"
    u.role = UserRole.super_admin
    u.lab_id = None
    u.lab = None
    u.created_at = datetime.utcnow()
    return u


@pytest.fixture
def member_user(lab):
    u = MagicMock(spec=User)
    u.id = uuid.uuid4()
    u.username = "member"
    u.role = UserRole.member
    u.lab_id = lab.id
    u.lab = lab
    u.created_at = datetime.utcnow()
    return u


@pytest.fixture
def lab_admin_user(lab):
    u = MagicMock(spec=User)
    u.id = uuid.uuid4()
    u.username = "lab_admin"
    u.role = UserRole.lab_admin
    u.lab_id = lab.id
    u.lab = lab
    u.created_at = datetime.utcnow()
    return u


# ── HTTP client fixture ───────────────────────────────────────────────────────

@pytest.fixture
def make_client():
    """
    Factory that yields an AsyncClient authenticated as *user* with *db* mocked.

    Usage:
        async with make_client(user, db) as client:
            resp = await client.get("/api/...")
    """
    overrides_snapshot = {}

    @asynccontextmanager
    async def _factory(user, db=None):
        _db = db or mock_db()
        app.dependency_overrides[get_db] = lambda: _db
        app.dependency_overrides[get_current_user] = lambda: user
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client, _db

    yield _factory
    app.dependency_overrides.clear()
