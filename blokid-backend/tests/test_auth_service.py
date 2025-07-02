# tests/test_auth_service.py
import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.models.user import User

class TestAuthService:
    def test_register_user_success(self, test_db: Session):
        """Test successful user registration"""
        auth_service = AuthService(test_db)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        user = auth_service.register_user(user_data)
        
        assert user.email == "test@example.com"
        assert user.is_active == True
        assert user.is_verified == False
        
        # Check organization was created
        assert len(user.owned_organizations) == 1
        assert user.owned_organizations[0].name == "test@example.com's Organization"
    
    def test_register_duplicate_email(self, test_db: Session):
        """Test registration with existing email"""
        auth_service = AuthService(test_db)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        # Register first user
        auth_service.register_user(user_data)
        
        # Try to register again with same email
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
    
    def test_authenticate_user_success(self, test_db: Session):
        """Test successful user authentication"""
        auth_service = AuthService(test_db)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        # Register user first
        registered_user = auth_service.register_user(user_data)
        
        # Authenticate
        authenticated_user = auth_service.authenticate_user("test@example.com", "testpass123")
        
        assert authenticated_user.id == registered_user.id
        assert authenticated_user.email == "test@example.com"
    
    def test_authenticate_user_wrong_password(self, test_db: Session):
        """Test authentication with wrong password"""
        auth_service = AuthService(test_db)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        # Register user first
        auth_service.register_user(user_data)
        
        # Try to authenticate with wrong password
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user("test@example.com", "wrongpassword")
        
        assert exc_info.value.status_code == 401
    
    def test_create_user_token(self, test_db: Session):
        """Test token creation for user"""
        auth_service = AuthService(test_db)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        user = auth_service.register_user(user_data)
        token = auth_service.create_user_token(user)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0