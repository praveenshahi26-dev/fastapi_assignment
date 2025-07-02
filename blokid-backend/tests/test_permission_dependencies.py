# tests/test_permission_dependencies.py
import pytest
from fastapi import HTTPException
from app.utils.dependencies import require_organization_admin, require_organization_access
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization

class TestPermissionDependencies:
    def test_require_organization_admin_success(self, test_db):
        """Test organization admin dependency success"""
        # Create test data
        user = User(email="admin3@example.com", hashed_password="hashed")
        test_db.add(user)
        test_db.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        test_db.add(org)
        test_db.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        test_db.add(membership)
        test_db.commit()
        
        # Test dependency
        dependency_func = require_organization_admin(org.id)
        result = dependency_func(current_user=user, db=test_db)
        
        assert result == user
    
    def test_require_organization_admin_forbidden(self, test_db):
        """Test organization admin dependency forbidden"""
        # Create test data
        admin = User(email="admin4@example.com", hashed_password="hashed")
        user = User(email="user3@example.com", hashed_password="hashed")
        test_db.add_all([admin, user])
        test_db.commit()
        
        org = Organization(name="Test Org", owner_id=admin.id)
        test_db.add(org)
        test_db.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_USER
        )
        test_db.add(membership)
        test_db.commit()
        
        # Test dependency
        dependency_func = require_organization_admin(org.id)
        
        with pytest.raises(HTTPException) as exc_info:
            dependency_func(current_user=user, db=test_db)
        
        assert exc_info.value.status_code == 403