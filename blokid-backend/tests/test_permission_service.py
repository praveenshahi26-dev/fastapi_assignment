# tests/test_permission_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.permission_service import PermissionService
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization

class TestPermissionService:
    def test_get_user_organization_role(self, test_db: Session):
        """Test getting user's organization role"""
        # Create test data
        user = User(email="test1@example.com", hashed_password="hashed")
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
        
        # Test
        permission_service = PermissionService(test_db)
        role = permission_service.get_user_organization_role(user.id, org.id)
        
        assert role == UserRole.ORGANIZATION_ADMIN
    
    def test_can_manage_organization_admin(self, test_db: Session):
        """Test organization admin can manage organization"""
        # Create test data
        user = User(email="admin1@example.com", hashed_password="hashed")
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
        
        # Test
        permission_service = PermissionService(test_db)
        can_manage = permission_service.can_manage_organization(user, org.id)
        
        assert can_manage == True
    
    def test_can_manage_organization_user_cannot(self, test_db: Session):
        """Test organization user cannot manage organization"""
        # Create test data
        admin = User(email="admin2@example.com", hashed_password="hashed")
        user = User(email="user2@example.com", hashed_password="hashed")
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
        
        # Test
        permission_service = PermissionService(test_db)
        can_manage = permission_service.can_manage_organization(user, org.id)
        
        assert can_manage == False