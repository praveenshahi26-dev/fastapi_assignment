# tests/test_security.py
from app.utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    verify_token
)
from datetime import timedelta

def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False

def test_jwt_token():
    """Test JWT token creation and verification"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded_email = verify_token(token)
    assert decoded_email == "test@example.com"

def test_invalid_token():
    """Test invalid token handling"""
    invalid_token = "invalid.token.here"
    result = verify_token(invalid_token)
    assert result is None