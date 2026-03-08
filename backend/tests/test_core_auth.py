"""Tests for core/auth.py — password utilities and JWT token handling."""
import pytest
from jose import jwt

from core.auth import hash_password, verify_password, create_access_token
from core.database import settings


def test_hash_password_is_not_plaintext():
    hashed = hash_password("secret123")
    assert hashed != "secret123"


def test_verify_password_correct():
    hashed = hash_password("correct_password")
    assert verify_password("correct_password", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("correct_password")
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token_contains_user_id(super_admin_user):
    token = create_access_token(super_admin_user)
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

    assert payload["sub"] == str(super_admin_user.id)
    assert payload["role"] == super_admin_user.role
    assert payload["lab_id"] is None
    assert payload["company_id"] is None
    assert "exp" in payload


def test_create_access_token_includes_lab_and_company(member_user):
    token = create_access_token(member_user)
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

    assert payload["sub"] == str(member_user.id)
    assert payload["lab_id"] == str(member_user.lab_id)
    assert payload["company_id"] == str(member_user.lab.company_id)
