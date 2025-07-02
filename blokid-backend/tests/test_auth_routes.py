# tests/test_auth_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from tests.conftest import test_db

@pytest.fixture
def test_client(test_db):
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    # Clean up
    app.dependency_overrides.clear()

class TestAuthRoutes:
    def test_register_user_success(self, test_client):
        """Test successful user registration"""
        user_data = {
            "email": "success@example.com",
            "password": "testpass123"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "success@example.com"
        assert data["is_active"] == True
        assert "id" in data
    
    def test_register_duplicate_email(self, test_client):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpass123"
        }
        
        # Register first user
        test_client.post("/auth/register", json=user_data)
        
        # Try to register again
        response = test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_login_success(self, test_client):
        """Test successful login"""
        # Register user first
        user_data = {
            "email": "login@example.com",
            "password": "testpass123"
        }
        test_client.post("/auth/register", json=user_data)
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "testpass123"
        }
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, test_client):
        """Test login with wrong password"""
        # Register user first
        user_data = {
            "email": "wrongpass@example.com",
            "password": "testpass123"
        }
        test_client.post("/auth/register", json=user_data)
        
        # Try to login with wrong password
        login_data = {
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        }
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user_info(self, test_client):
        """Test getting current user info"""
        # Register and login user
        user_data = {
            "email": "current@example.com",
            "password": "testpass123"
        }
        test_client.post("/auth/register", json=user_data)
        
        login_response = test_client.post("/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current@example.com"
    
    def test_get_current_user_info_unauthorized(self, test_client):
        """Test getting user info without token"""
        response = test_client.get("/auth/me")
        assert response.status_code == 403  # No authorization header