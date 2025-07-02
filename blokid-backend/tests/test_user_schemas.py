# tests/test_user_schemas.py
from app.schemas.user import UserCreate, UserLogin, Token
from app.models.user import UserRole

def test_user_create_schema():
    """Test UserCreate schema validation"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    assert user.password == "testpassword123"

def test_user_login_schema():
    """Test UserLogin schema validation"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    login = UserLogin(**login_data)
    assert login.email == "test@example.com"

def test_token_schema():
    """Test Token schema validation"""
    token_data = {
        "access_token": "sample_token",
        "token_type": "bearer"
    }
    token = Token(**token_data)
    assert token.access_token == "sample_token"
    assert token.token_type == "bearer"