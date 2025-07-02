# tests/test_organization_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization

client = TestClient(app)

class TestOrganizationRoutes:
    def test_create_organization(self, db_session, auth_headers):
        """Test creating organization via API"""
        org_data = {
            "name": "Test Organization",
            "description": "A test organization"
        }
        
        response = client.post(
            "/organizations/",
            json=org_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json()["name"] == "Test Organization"
    
    def test_get_user_organizations(self, db_session, auth_headers):
        """Test getting user organizations"""
        response = client.get("/organizations/", headers=auth_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_organization_unauthorized(self, db_session):
        """Test getting organization without authentication"""
        response = client.get("/organizations/1")
        
        assert response.status_code == 401