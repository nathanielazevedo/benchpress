"""Integration tests for POST /api/auth/login and GET /api/auth/me."""
import pytest
from unittest.mock import AsyncMock

from core.auth import hash_password
from tests.conftest import mock_db, mock_result


async def test_login_returns_token_on_valid_credentials(make_client, super_admin_user):
    # Arrange: DB returns the user when queried by username
    super_admin_user.password_hash = hash_password("correct_password")
    db = mock_db()
    db.execute = AsyncMock(return_value=mock_result(scalar=super_admin_user))

    async with make_client(super_admin_user, db) as (client, _):
        resp = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "correct_password"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_returns_401_on_wrong_password(make_client, super_admin_user):
    super_admin_user.password_hash = hash_password("correct_password")
    db = mock_db()
    db.execute = AsyncMock(return_value=mock_result(scalar=super_admin_user))

    async with make_client(super_admin_user, db) as (client, _):
        resp = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong_password"},
        )

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid username or password"


async def test_login_returns_401_when_user_not_found(make_client, super_admin_user):
    db = mock_db()
    db.execute = AsyncMock(return_value=mock_result(scalar=None))  # user not found

    async with make_client(super_admin_user, db) as (client, _):
        resp = await client.post(
            "/api/auth/login",
            json={"username": "nobody", "password": "anything"},
        )

    assert resp.status_code == 401


async def test_me_returns_current_user_profile(make_client, member_user):
    async with make_client(member_user) as (client, _):
        resp = await client.get("/api/auth/me")

    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == member_user.username
    assert body["role"] == member_user.role.value


async def test_me_returns_401_without_auth():
    """No dependency override — the real bearer auth runs and rejects the request."""
    from httpx import AsyncClient, ASGITransport
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/api/auth/me")

    assert resp.status_code == 401  # HTTPBearer returns 401 when Authorization header is absent
