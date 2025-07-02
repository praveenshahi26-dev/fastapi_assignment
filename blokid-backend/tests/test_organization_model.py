#  tests/test_organization_model.py
from app.models.organization import Organization
from app.models.user import User
from app.models.website import Website
from app.database import Base, engine

def test_organization_model_creation():
    """Test Organization model can be created"""
    org = Organization(
        name="Test Organization",
        description="A test organization",
        owner_id=1
    )
    assert org.name == "Test Organization"
    assert org.description == "A test organization"
    assert org.owner_id == 1