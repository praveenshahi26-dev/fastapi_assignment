# tests/test_user_model.py
from app.models.user import User, UserRole, OrganizationMember
from app.database import Base, engine
import pytest

def test_user_model_creation():
    """Test User model can be created"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_here"
    )
    assert user.email == "test@example.com"
    assert user.is_active == True
    assert user.is_verified == False
    assert user.created_at is not None

def test_user_role_enum():
    """Test UserRole enum values"""
    assert UserRole.ORGANIZATION_ADMIN.value == "organization_admin"
    assert UserRole.ORGANIZATION_USER.value == "organization_user"