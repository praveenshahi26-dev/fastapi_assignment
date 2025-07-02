# tests/test_organization_schemas.py
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

def test_organization_create_schema():
    """Test OrganizationCreate schema validation"""
    org_data = {
        "name": "Test Organization",
        "description": "A test organization"
    }
    org = OrganizationCreate(**org_data)
    assert org.name == "Test Organization"
    assert org.description == "A test organization"

def test_organization_update_schema():
    """Test OrganizationUpdate schema validation"""
    update_data = {
        "name": "Updated Organization"
    }
    org_update = OrganizationUpdate(**update_data)
    assert org_update.name == "Updated Organization"
    assert org_update.description is None