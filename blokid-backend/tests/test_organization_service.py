# tests/test_organization_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.organization_service import OrganizationService
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.models.user import User, UserRole
from app.models.organization import Organization

class TestOrganizationService:
    def test_create_organization(self, test_db: Session):
        """Test creating an organization"""
        # Create user
        user = User(email="test_org_delete@example.com", hashed_password="hashed")
        test_db.add(user)
        test_db.commit()
        
        # Create organization
        org_service = OrganizationService(test_db)
        org_data = OrganizationCreate(
            name="Test Organization",
            description="A test organization"
        )
        
        organization = org_service.create_organization(org_data, user)
        
        assert organization.name == "Test Organization"
        assert organization.description == "A test organization"
        assert organization.owner_id == user.id
    
    def test_get_organization_success(self, test_db: Session):
        """Test getting an organization with proper permissions"""
        # Create test data
        user = User(email="test_org_delete@example.com", hashed_password="hashed")
        test_db.add(user)
        test_db.commit()
        
        org_service = OrganizationService(test_db)
        org_data = OrganizationCreate(name="Test Org")
        organization = org_service.create_organization(org_data, user)
        
        # Get organization
        retrieved_org = org_service.get_organization(organization.id, user)
        
        assert retrieved_org.id == organization.id
        assert retrieved_org.name == "Test Org"
    
    def test_update_organization(self, test_db: Session):
        """Test updating an organization"""
        # Create test data
        user = User(email="test_org_delete@example.com", hashed_password="hashed")
        test_db.add(user)
        test_db.commit()
        
        org_service = OrganizationService(test_db)
        org_data = OrganizationCreate(name="Original Name")
        organization = org_service.create_organization(org_data, user)
        
        # Update organization
        update_data = OrganizationUpdate(name="Updated Name")
        updated_org = org_service.update_organization(organization.id, update_data, user)
        
        assert updated_org.name == "Updated Name"
    
    def test_delete_organization(self, test_db: Session):
        """Test deleting an organization"""
        # Create test data
        user = User(email="test_org_delete@example.com", hashed_password="hashed")
        test_db.add(user)
        test_db.commit()
        
        org_service = OrganizationService(test_db)
        org_data = OrganizationCreate(name="To Delete")
        organization = org_service.create_organization(org_data, user)
        
        # Delete organization
        result = org_service.delete_organization(organization.id, user)
        
        assert result == True
        
        # Verify deletion
        deleted_org = test_db.query(Organization).filter(
            Organization.id == organization.id
        ).first()
        assert deleted_org is None