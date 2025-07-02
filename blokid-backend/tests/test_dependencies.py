# tests/test_dependencies.py
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import pytest
from unittest.mock import Mock, MagicMock
from app.utils.dependencies import get_current_user
from app.models.user import User

def test_get_current_user_valid_token():
    """Test get_current_user with valid token"""
    # Mock dependencies
    mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
    mock_credentials.credentials = "valid_token"
    
    mock_db = MagicMock()
    mock_user = User(id=1, email="test@example.com", hashed_password="hashed")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Mock verify_token to return email
    with pytest.MonkeyPatch().context() as m:
        m.setattr("app.utils.dependencies.verify_token", lambda x: "test@example.com")
        
        result = get_current_user(mock_credentials, mock_db)
        assert result == mock_user

def test_get_current_user_invalid_token():
    """Test get_current_user with invalid token"""
    mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
    mock_credentials.credentials = "invalid_token"
    
    mock_db = MagicMock()
    
    # Mock verify_token to return None
    with pytest.MonkeyPatch().context() as m:
        m.setattr("app.utils.dependencies.verify_token", lambda x: None)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_credentials, mock_db)
        
        assert exc_info.value.status_code == 401