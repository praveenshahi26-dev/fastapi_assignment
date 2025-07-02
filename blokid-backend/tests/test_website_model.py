# tests/test_website_model.py
from app.models.website import Website

def test_website_model_creation():
    """Test Website model can be created"""
    website = Website(
        name="Test Website",
        url="https://test.com",
        description="A test website",
        organization_id=1
    )
    assert website.name == "Test Website"
    assert website.url == "https://test.com"
    assert website.organization_id == 1