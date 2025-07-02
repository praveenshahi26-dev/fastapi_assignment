# tests/test_website_schemas.py
from app.schemas.website import WebsiteCreate, WebsiteUpdate

def test_website_create_schema():
    """Test WebsiteCreate schema validation"""
    website_data = {
        "name": "Test Website",
        "url": "https://test.com",
        "description": "A test website",
        "organization_id": 1
    }
    website = WebsiteCreate(**website_data)
    assert website.name == "Test Website"
    assert website.url == "https://test.com"
    assert website.organization_id == 1

def test_website_update_schema():
    """Test WebsiteUpdate schema validation"""
    update_data = {
        "name": "Updated Website"
    }
    website_update = WebsiteUpdate(**update_data)
    assert website_update.name == "Updated Website"
    assert website_update.url is None