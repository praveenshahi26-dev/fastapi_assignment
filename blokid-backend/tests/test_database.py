from app.database import get_db, engine
from sqlalchemy import text
import pytest

def test_database_connection():
    """Test database connection works"""
    db = next(get_db())
    result = db.execute(text("SELECT 1"))
    assert result.fetchone()[0] == 1
    db.close()

def test_engine_connection():
    """Test engine connection"""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
