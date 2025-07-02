import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import Depends
from sqlalchemy.orm import Session
import os
from datetime import timedelta

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization
from app.utils.security import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def test_db():
    # Create a database session
    db = TestingSessionLocal()
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        yield db
    finally:
        # Rollback any changes
        db.rollback()
        # Close the session
        db.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(test_db):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture()
def auth_headers(test_db):
    """Fixture to create an authenticated user and return auth headers"""
    # Create a test user
    hashed_password = get_password_hash("testpassword123")
    user = User(
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create an organization for the user
    organization = Organization(
        name="Test Org",
        description="Test Organization",
        owner_id=user.id
    )
    test_db.add(organization)
    test_db.commit()
    test_db.refresh(organization)
    
    # Add user as organization admin
    membership = OrganizationMember(
        user_id=user.id,
        organization_id=organization.id,
        role=UserRole.ORGANIZATION_ADMIN
    )
    test_db.add(membership)
    test_db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"Authorization": f"Bearer {access_token}"}
