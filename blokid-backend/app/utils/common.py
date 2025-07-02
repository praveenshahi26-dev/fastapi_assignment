from typing import Optional
from datetime import datetime
import uuid

def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())

def get_timestamp() -> datetime:
    """Get current timestamp with timezone"""
    return datetime.now()

def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO 8601 string with timezone"""
    return dt.isoformat()

def validate_email(email: str) -> bool:
    """Basic email validation"""
    if "@" not in email:
        return False
    return True

def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
