# tests/test_permission_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.permission_service import PermissionService
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization

class TestPermissionService:
    def test_get_user_organization_role(self, db_session: Session):
        """Test getting user's organization role"""
        # Create test data
        user = User(email="test@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test
        permission_service = PermissionService(db_session)
        role = permission_service.get_user_organization_role(user.id, org.id)
        
        assert role == UserRole.ORGANIZATION_ADMIN
    
    def test_can_manage_organization_admin(self, db_session: Session):
        """Test organization admin can manage organization"""
        # Create test data
        user = User(email="admin@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test
        permission_service = PermissionService(db_session)
        can_manage = permission_service.can_manage_organization(user, org.id)
        
        assert can_manage == True
    
    def test_can_manage_organization_user_cannot(self, db_session: Session):
        """Test organization user cannot manage organization"""
        # Create test data
        admin = User(email="admin@example.com", hashed_password="hashed")
        user = User(email="user@example.com", hashed_password="hashed")
        db_session.add_all([admin, user])
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=admin.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_USER
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test
        permission_service = PermissionService(db_session)
        can_manage = permission_service.can_manage_organization(user, org.id)
        
        assert can_manage == False