# tests/test_website_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.website_service import WebsiteService
from app.schemas.website import WebsiteCreate, WebsiteUpdate
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.website import Website

class TestWebsiteService:
    def test_create_website(self, test_db: Session):
        """Test creating a website"""
        # Create user and organization
        user = User(
            email="test@example.com", 
            hashed_password="hashed",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        test_db.add(org)
        test_db.commit()
        
        # Add user as organization admin
        from app.models.user import OrganizationMember
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        test_db.add(membership)
        test_db.commit()
        
        # Create website
        website_service = WebsiteService(test_db)
        website_data = WebsiteCreate(
            name="Test Website",
            description="A test website",
            url="https://test.com",
            organization_id=org.id
        )
        
        website = website_service.create_website(website_data, user)
        
        assert website.name == "Test Website"
        assert website.organization_id == org.id
    
    def test_get_organization_websites(self, test_db: Session):
        """Test getting organization websites"""
        # Create test data
        user = User(
            email="test@example.com", 
            hashed_password="hashed",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        test_db.add(org)
        test_db.commit()
        
        # Add user as organization admin
        from app.models.user import OrganizationMember
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        test_db.add(membership)
        test_db.commit()
        
        website = Website(
            name="Test Website",
            url="https://test.com",
            organization_id=org.id
        )
        test_db.add(website)
        test_db.commit()
        
        # Get websites
        website_service = WebsiteService(test_db)
        websites = website_service.get_organization_websites(org.id, user)
        
        assert len(websites) == 1
        assert websites[0].name == "Test Website"