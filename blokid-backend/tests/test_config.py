# tests/test_config.py
from app.config import settings

def test_config_loads():
    """Test that configuration loads properly"""
    assert settings.DATABASE_URL is not None
    assert settings.SECRET_KEY is not None
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    # assert settings.SMTP_SERVER == "smtp.gmail.com"
    # assert settings.SMTP_PORT == 465
    # assert settings.SMTP_USERNAME == "praveenshahi26@gmail.com"
    # assert settings.SMTP_PASSWORD == "ptjrrxcbyqoawkxn"