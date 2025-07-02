# tests/test_organization_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization

client = TestClient(app)

class TestOrganizationRoutes:
    def test_create_organization(self, test_db, auth_headers):
        """Test creating organization via API"""
        org_data = {
            "name": "Test Organization",
            "description": "A test organization"
        }
        
        response = client.post(
            "/api/organizations/",
            json=org_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json()["name"] == "Test Organization"
    
    def test_get_user_organizations(self, test_db, auth_headers):
        """Test getting user organizations"""
        response = client.get("/api/organizations/", headers=auth_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_organization_unauthorized(self, test_db):
        """Test getting organization without authentication"""
        response = client.get("/api/organizations/999")
        
        # Should return 403 Forbidden because the endpoint requires authentication
        assert response.status_code == 403