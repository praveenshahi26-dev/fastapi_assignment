# BlokID Backend Implementation Guide

## Project Overview
Build a FastAPI backend with user authentication, organizations, and websites management with role-based permissions.

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT Authentication
- Pytest

---

## Phase 1: Project Setup (Day 1 - Part 1)

### Task 1.1: Initialize Project Structure
**Estimated Time: 30 minutes**

Create the following project structure:
```
blokid-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   └── website.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   └── website.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── organizations.py
│   │   └── websites.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── email_service.py
│   │   └── permission_service.py
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       └── dependencies.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_auth.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

**Test Task 1.1:**
```python
# tests/test_project_structure.py
import os

def test_project_structure():
    """Test that all required directories and files exist"""
    required_paths = [
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "app/models/user.py",
        "app/schemas/user.py",
        "app/routers/auth.py"
    ]
    
    for path in required_paths:
        assert os.path.exists(path), f"Missing required file: {path}"
```

### Task 1.2: Setup Dependencies and Configuration
**Estimated Time: 45 minutes**

**File: requirements.txt**
```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.0.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
python-dotenv==1.0.0
```

**File: app/config.py**
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/blokid_db"
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email (for future implementation)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**File: .env.example**
```env
DATABASE_URL=postgresql://user:password@localhost/blokid_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Test Task 1.2:**
```python
# tests/test_config.py
from app.config import settings

def test_config_loads():
    """Test that configuration loads properly"""
    assert settings.database_url is not None
    assert settings.secret_key is not None
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes > 0
```

---

## Phase 2: Database Setup (Day 1 - Part 2)

### Task 2.1: Database Connection Setup
**Estimated Time: 30 minutes**

**File: app/database.py**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Test Task 2.1:**
```python
# tests/test_database.py
from app.database import get_db, engine
from sqlalchemy import text

def test_database_connection():
    """Test database connection works"""
    db = next(get_db())
    result = db.execute(text("SELECT 1"))
    assert result.fetchone()[0] == 1
    db.close()
```

### Task 2.2: User Model
**Estimated Time: 1 hour**

**File: app/models/user.py**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(enum.Enum):
    ORGANIZATION_ADMIN = "organization_admin"
    ORGANIZATION_USER = "organization_user"
    WEBSITE_ADMIN = "website_admin"
    WEBSITE_USER = "website_user"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owned_organizations = relationship("Organization", back_populates="owner")
    organization_memberships = relationship("OrganizationMember", back_populates="user")
    website_memberships = relationship("WebsiteMember", back_populates="user")

class OrganizationMember(Base):
    __tablename__ = "organization_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="organization_memberships")
    organization = relationship("Organization", back_populates="members")

class WebsiteMember(Base):
    __tablename__ = "website_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="website_memberships")
    website = relationship("Website", back_populates="members")
```

**Test Task 2.2:**
```python
# tests/test_user_model.py
from app.models.user import User, UserRole, OrganizationMember
from app.database import Base, engine
import pytest

def test_user_model_creation():
    """Test User model can be created"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_here"
    )
    assert user.email == "test@example.com"
    assert user.is_active == True
    assert user.is_verified == False

def test_user_role_enum():
    """Test UserRole enum values"""
    assert UserRole.ORGANIZATION_ADMIN.value == "organization_admin"
    assert UserRole.ORGANIZATION_USER.value == "organization_user"
```

### Task 2.3: Organization Model
**Estimated Time: 45 minutes**

**File: app/models/organization.py**
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_organizations")
    members = relationship("OrganizationMember", back_populates="organization")
    websites = relationship("Website", back_populates="organization")
```

**Test Task 2.3:**
```python
# tests/test_organization_model.py
from app.models.organization import Organization

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
```

### Task 2.4: Website Model
**Estimated Time: 45 minutes**

**File: app/models/website.py**
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="websites")
    members = relationship("WebsiteMember", back_populates="website")
```

**Test Task 2.4:**
```python
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
```

---

## Phase 3: Pydantic Schemas (Day 1 - Part 3)

### Task 3.1: User Schemas
**Estimated Time: 1 hour**

**File: app/schemas/user.py**
```python
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class OrganizationMemberBase(BaseModel):
    user_id: int
    organization_id: int
    role: UserRole

class OrganizationMemberCreate(OrganizationMemberBase):
    pass

class OrganizationMember(OrganizationMemberBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WebsiteMemberBase(BaseModel):
    user_id: int
    website_id: int
    role: UserRole

class WebsiteMemberCreate(WebsiteMemberBase):
    pass

class WebsiteMember(WebsiteMemberBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**Test Task 3.1:**
```python
# tests/test_user_schemas.py
from app.schemas.user import UserCreate, UserLogin, Token
from app.models.user import UserRole

def test_user_create_schema():
    """Test UserCreate schema validation"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    assert user.password == "testpassword123"

def test_user_login_schema():
    """Test UserLogin schema validation"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    login = UserLogin(**login_data)
    assert login.email == "test@example.com"

def test_token_schema():
    """Test Token schema validation"""
    token_data = {
        "access_token": "sample_token",
        "token_type": "bearer"
    }
    token = Token(**token_data)
    assert token.access_token == "sample_token"
    assert token.token_type == "bearer"
```

### Task 3.2: Organization Schemas
**Estimated Time: 45 minutes**

**File: app/schemas/organization.py**
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import User

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class OrganizationInDB(OrganizationBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Organization(OrganizationInDB):
    owner: Optional[User] = None
    # members: Optional[List[OrganizationMember]] = None

class OrganizationWithMembers(Organization):
    members: Optional[List['OrganizationMember']] = None

# Import after to avoid circular imports
from app.schemas.user import OrganizationMember
OrganizationWithMembers.model_rebuild()
```

**Test Task 3.2:**
```python
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
```

### Task 3.3: Website Schemas
**Estimated Time: 45 minutes**

**File: app/schemas/website.py**
```python
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.schemas.organization import Organization

class WebsiteBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None

class WebsiteCreate(WebsiteBase):
    organization_id: int

class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

class WebsiteInDB(WebsiteBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Website(WebsiteInDB):
    organization: Optional[Organization] = None

class WebsiteWithMembers(Website):
    members: Optional[List['WebsiteMember']] = None

# Import after to avoid circular imports
from app.schemas.user import WebsiteMember
WebsiteWithMembers.model_rebuild()
```

**Test Task 3.3:**
```python
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
```

---

## Phase 4: Authentication & Security (Day 2 - Part 1)

### Task 4.1: Security Utilities
**Estimated Time: 1 hour**

**File: app/utils/security.py**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
```

**Test Task 4.1:**
```python
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
```

### Task 4.2: Authentication Dependencies
**Estimated Time: 45 minutes**

**File: app/utils/dependencies.py**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.security import verify_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = verify_token(credentials.credentials)
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

**Test Task 4.2:**
```python
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
```

---

## Phase 5: Authentication Routes (Day 2 - Part 2)

### Task 5.1: Authentication Service
**Estimated Time: 1 hour**

**File: app/services/auth_service.py**
```python
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_create: UserCreate) -> User:
        """Register a new user and create their organization"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Create organization for the user
        organization = Organization(
            name=f"{user_create.email}'s Organization",
            description="Default organization",
            owner_id=db_user.id
        )
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        
        # Add user as organization admin
        org_membership = OrganizationMember(
            user_id=db_user.id,
            organization_id=organization.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        self.db.add(org_membership)
        self.db.commit()
        
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate a user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    
    def create_user_token(self, user: User) -> str:
        """Create access token for user"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return access_token
```

**Test Task 5.1:**
```python
# tests/test_auth_service.py
import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.models.user import User

class TestAuthService:
    def test_register_user_success(self, db_session: Session):
        """Test successful user registration"""
        auth_service = AuthService(db_session)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        user = auth_service.register_user(user_data)
        
        assert user.email == "test@example.com"
        assert user.is_active == True
        assert user.is_verified == False
        
        # Check organization was created
        assert len(user.owned_organizations) == 1
        assert user.owned_organizations[0].name == "test@example.com's Organization"
    
    def test_register_duplicate_email(self, db_session: Session):
        """Test registration with existing email"""
        auth_service = AuthService(db_session)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        # Register first user
        auth_service.register_user(user_data)
        
        # Try to register again with same email
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
    
    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication"""
        auth_service = AuthService(db_session)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        # Register user first
        registered_user = auth_service.register_user(user_data)
        
        # Authenticate
        authenticated_user = auth_service.authenticate_user("test@example.com", "testpass123")
        
        assert authenticated_user.id == registered_user.id
        assert authenticated_user.email == "test@example.com"
    
    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test authentication with wrong password"""
        auth_service = AuthService(db_session)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        # Register user first
        auth_service.register_user(user_data)
        
        # Try to authenticate with wrong password
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user("test@example.com", "wrongpassword")
        
        assert exc_info.value.status_code == 401
    
    def test_create_user_token(self, db_session: Session):
        """Test token creation for user"""
        auth_service = AuthService(db_session)
        user_data = UserCreate(email="test@example.com", password="testpass123")
        
        user = auth_service.register_user(user_data)
        token = auth_service.create_user_token(user)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
```

### Task 5.2: Authentication Routes
**Estimated Time: 1 hour**

**File: app/routers/auth.py**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token, User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    return auth_service.register_user(user_create)

@router.post("/login", response_model=Token)
def login_user(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(user_login.email, user_login.password)
    
    # Create token
    access_token = auth_service.create_user_token(user)
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user

@router.post("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email (placeholder for future implementation)"""
    # TODO: Implement email verification logic
    return {"message": "Email verification not implemented yet"}
```

**Test Task 5.2:**
```python
# tests/test_auth_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthRoutes:
    def test_register_user_success(self):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["is_active"] == True
        assert "id" in data
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpass123"
        }
        
        # Register first user
        client.post("/auth/register", json=user_data)
        
        # Try to register again
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_login_success(self):
        """Test successful login"""
        # Register user first
        user_data = {
            "email": "login@example.com",
            "password": "testpass123"
        }
        client.post("/auth/register", json=user_data)
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "testpass123"
        }
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register user first
        user_data = {
            "email": "wrongpass@example.com",
            "password": "testpass123"
        }
        client.post("/auth/register", json=user_data)
        
        # Try to login with wrong password
        login_data = {
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user_info(self):
        """Test getting current user info"""
        # Register and login user
        user_data = {
            "email": "current@example.com",
            "password": "testpass123"
        }
        client.post("/auth/register", json=user_data)
        
        login_response = client.post("/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current@example.com"
    
    def test_get_current_user_info_unauthorized(self):
        """Test getting user info without token"""
        response = client.get("/auth/me")
        assert response.status_code == 403  # No authorization header
```

---

## Phase 6: Permission System (Day 2 - Part 3)

### Task 6.1: Permission Service
**Estimated Time: 1.5 hours**

**File: app/services/permission_service.py**
```python
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, OrganizationMember, WebsiteMember, UserRole
from app.models.organization import Organization
from app.models.website import Website
from typing import List

class PermissionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_organization_role(self, user_id: int, organization_id: int) -> UserRole:
        """Get user's role in an organization"""
        membership = self.db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organization"
            )
        
        return membership.role
    
    def get_user_website_role(self, user_id: int, website_id: int) -> UserRole:
        """Get user's role for a website"""
        membership = self.db.query(WebsiteMember).filter(
            WebsiteMember.user_id == user_id,
            WebsiteMember.website_id == website_id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this website"
            )
        
        return membership.role
    
    def can_manage_organization(self, user: User, organization_id: int) -> bool:
        """Check if user can manage (CRUD) an organization"""
        try:
            role = self.get_user_organization_role(user.id, organization_id)
            return role == UserRole.ORGANIZATION_ADMIN
        except HTTPException:
            return False
    
    def can_read_organization(self, user: User, organization_id: int) -> bool:
        """Check if user can read an organization"""
        try:
            role = self.get_user_organization_role(user.id, organization_id)
            return role in [UserRole.ORGANIZATION_ADMIN, UserRole.ORGANIZATION_USER]
        except HTTPException:
            return False
    
    def can_update_organization(self, user: User, organization_id: int) -> bool:
        """Check if user can update an organization"""
        try:
            role = self.get_user_organization_role(user.id, organization_id)
            return role in [UserRole.ORGANIZATION_ADMIN, UserRole.ORGANIZATION_USER]
        except HTTPException:
            return False
    
    def can_manage_website(self, user: User, website_id: int) -> bool:
        """Check if user can manage (CRUD) a website"""
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            return False
        
        # Check organization-level permissions first
        if self.can_manage_organization(user, website.organization_id):
            return True
        
        # Check website-level permissions
        try:
            role = self.get_user_website_role(user.id, website_id)
            return role == UserRole.WEBSITE_ADMIN
        except HTTPException:
            return False
    
    def can_read_website(self, user: User, website_id: int) -> bool:
        """Check if user can read a website"""
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            return False
        
        # Check organization-level permissions first
        if self.can_read_organization(user, website.organization_id):
            return True
        
        # Check website-level permissions
        try:
            role = self.get_user_website_role(user.id, website_id)
            return role in [UserRole.WEBSITE_ADMIN, UserRole.WEBSITE_USER]
        except HTTPException:
            return False
    
    def can_update_website(self, user: User, website_id: int) -> bool:
        """Check if user can update a website"""
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            return False
        
        # Check organization-level permissions first
        if self.can_manage_organization(user, website.organization_id):
            return True
        
        # Check website-level permissions
        try:
            role = self.get_user_website_role(user.id, website_id)
            return role in [UserRole.WEBSITE_ADMIN, UserRole.WEBSITE_USER]
        except HTTPException:
            return False
    
    def can_create_website_in_organization(self, user: User, organization_id: int) -> bool:
        """Check if user can create websites in an organization"""
        try:
            role = self.get_user_organization_role(user.id, organization_id)
            return role in [UserRole.ORGANIZATION_ADMIN, UserRole.ORGANIZATION_USER]
        except HTTPException:
            return False
    
    def get_user_organizations(self, user: User) -> List[Organization]:
        """Get all organizations user has access to"""
        memberships = self.db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user.id
        ).all()
        
        organization_ids = [m.organization_id for m in memberships]
        return self.db.query(Organization).filter(
            Organization.id.in_(organization_ids)
        ).all()
    
    def get_user_websites(self, user: User) -> List[Website]:
        """Get all websites user has access to"""
        # Get websites through organization membership
        org_memberships = self.db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user.id
        ).all()
        
        org_website_ids = []
        for membership in org_memberships:
            websites = self.db.query(Website).filter(
                Website.organization_id == membership.organization_id
            ).all()
            org_website_ids.extend([w.id for w in websites])
        
        # Get websites through direct website membership
        website_memberships = self.db.query(WebsiteMember).filter(
            WebsiteMember.user_id == user.id
        ).all()
        
        direct_website_ids = [m.website_id for m in website_memberships]
        
        # Combine and deduplicate
        all_website_ids = list(set(org_website_ids + direct_website_ids))
        
        return self.db.query(Website).filter(
            Website.id.in_(all_website_ids)
        ).all()
```

**Test Task 6.1:**
```python
# tests/test_permission_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.permission_service import PermissionService
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization

class TestPermissionService:
    def test_get_user_organization_role(self, db_session: Session):
        """Test getting user's organization role"""
        # Create test data
        user = User(email="test@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test
        permission_service = PermissionService(db_session)
        role = permission_service.get_user_organization_role(user.id, org.id)
        
        assert role == UserRole.ORGANIZATION_ADMIN
    
    def test_can_manage_organization_admin(self, db_session: Session):
        """Test organization admin can manage organization"""
        # Create test data
        user = User(email="admin@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test
        permission_service = PermissionService(db_session)
        can_manage = permission_service.can_manage_organization(user, org.id)
        
        assert can_manage == True
    
    def test_can_manage_organization_user_cannot(self, db_session: Session):
        """Test organization user cannot manage organization"""
        # Create test data
        admin = User(email="admin@example.com", hashed_password="hashed")
        user = User(email="user@example.com", hashed_password="hashed")
        db_session.add_all([admin, user])
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=admin.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_USER
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test
        permission_service = PermissionService(db_session)
        can_manage = permission_service.can_manage_organization(user, org.id)
        
        assert can_manage == False
```

### Task 6.2: Permission Dependencies
**Estimated Time: 45 minutes**

**File: app/utils/dependencies.py** (Update existing file)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.permission_service import PermissionService
from app.utils.security import verify_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = verify_token(credentials.credentials)
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_organization_admin(organization_id: int):
    """Dependency to require organization admin role"""
    def _require_organization_admin(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        permission_service = PermissionService(db)
        if not permission_service.can_manage_organization(current_user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization admin access required"
            )
        return current_user
    return _require_organization_admin

def require_organization_access(organization_id: int):
    """Dependency to require any organization access"""
    def _require_organization_access(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        permission_service = PermissionService(db)
        if not permission_service.can_read_organization(current_user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization access required"
            )
        return current_user
    return _require_organization_access

def require_website_admin(website_id: int):
    """Dependency to require website admin role"""
    def _require_website_admin(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        permission_service = PermissionService(db)
        if not permission_service.can_manage_website(current_user, website_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Website admin access required"
            )
        return current_user
    return _require_website_admin

def require_website_access(website_id: int):
    """Dependency to require any website access"""
    def _require_website_access(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        permission_service = PermissionService(db)
        if not permission_service.can_read_website(current_user, website_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Website access required"
            )
        return current_user
    return _require_website_access
```

**Test Task 6.2:**
```python
# tests/test_permission_dependencies.py
import pytest
from fastapi import HTTPException
from app.utils.dependencies import require_organization_admin, require_organization_access
from app.models.user import User, OrganizationMember, UserRole
from app.models.organization import Organization

class TestPermissionDependencies:
    def test_require_organization_admin_success(self, db_session):
        """Test organization admin dependency success"""
        # Create test data
        user = User(email="admin@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=user.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test dependency
        dependency_func = require_organization_admin(org.id)
        result = dependency_func(current_user=user, db=db_session)
        
        assert result == user
    
    def test_require_organization_admin_forbidden(self, db_session):
        """Test organization admin dependency forbidden"""
        # Create test data
        admin = User(email="admin@example.com", hashed_password="hashed")
        user = User(email="user@example.com", hashed_password="hashed")
        db_session.add_all([admin, user])
        db_session.commit()
        
        org = Organization(name="Test Org", owner_id=admin.id)
        db_session.add(org)
        db_session.commit()
        
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=UserRole.ORGANIZATION_USER
        )
        db_session.add(membership)
        db_session.commit()
        
        # Test dependency
        dependency_func = require_organization_admin(org.id)
        
        with pytest.raises(HTTPException) as exc_info:
            dependency_func(current_user=user, db=db_session)
        
        assert exc_info.value.status_code == 403
```

---

## Phase 7: Organization Management (Day 3 - Part 1)

### Task 7.1: Organization Service
**Estimated Time: 1 hour**

**File: app/services/organization_service.py**
```python
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.organization import Organization
from app.models.user import User, OrganizationMember, UserRole
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.services.permission_service import PermissionService
from typing import List

class OrganizationService:
    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)
    
    def create_organization(self, org_create: OrganizationCreate, user: User) -> Organization:
        """Create a new organization"""
        organization = Organization(
            name=org_create.name,
            description=org_create.description,
            owner_id=user.id
        )
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        
        # Add user as organization admin
        membership = OrganizationMember(
            user_id=user.id,
            organization_id=organization.id,
            role=UserRole.ORGANIZATION_ADMIN
        )
        self.db.add(membership)
        self.db.commit()
        
        return organization
    
    def get_organization(self, organization_id: int, user: User) -> Organization:
        """Get an organization by ID"""
        if not self.permission_service.can_read_organization(user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this organization"
            )
        
        organization = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return organization
    
    def get_user_organizations(self, user: User) -> List[Organization]:
        """Get all organizations for a user"""
        return self.permission_service.get_user_organizations(user)
    
    def update_organization(
        self, 
        organization_id: int, 
        org_update: OrganizationUpdate, 
        user: User
    ) -> Organization:
        """Update an organization"""
        if not self.permission_service.can_update_organization(user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this organization"
            )
        
        organization = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Update fields
        update_data = org_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        self.db.commit()
        self.db.refresh(organization)
        
        return organization
    
    def delete_organization(self, organization_id: int, user: User) -> bool:
        """Delete an organization"""
        if not self.permission_service.can_manage_organization(user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this organization"
            )
        
        organization = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Delete associated memberships first
        self.db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == organization_id
        ).delete()
        
        # Delete organization
        self.db.delete(organization)
        self.db.commit()
        
        return True
    
    def invite_user_to_organization(
        self, 
        organization_id: int, 
        user_email: str, 
        role: UserRole, 
        inviter: User
    ) -> OrganizationMember:
        """Invite a user to an organization"""
        if not self.permission_service.can_manage_organization(inviter, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to invite users to this organization"
            )
        
        # Find user to invite
        user_to_invite = self.db.query(User).filter(User.email == user_email).first()
        if not user_to_invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is already a member
        existing_membership = self.db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_to_invite.id,
            OrganizationMember.organization_id == organization_id
        ).first()
        
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization"
            )
        
        # Create membership
        membership = OrganizationMember(
            user_id=user_to_invite.id,
            organization_id=organization_id,
            role=role
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        
        return membership
```

**Test Task 7.1:**
```python
# tests/test_organization_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.organization_service import OrganizationService
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.models.user import User, UserRole
from app.models.organization import Organization

class TestOrganizationService:
    def test_create_organization(self, db_session: Session):
        """Test creating an organization"""
        # Create user
        user = User(email="test@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        # Create organization
        org_service = OrganizationService(db_session)
        org_data = OrganizationCreate(
            name="Test Organization",
            description="A test organization"
        )
        
        organization = org_service.create_organization(org_data, user)
        
        assert organization.name == "Test Organization"
        assert organization.description == "A test organization"
        assert organization.owner_id == user.id
    
    def test_get_organization_success(self, db_session: Session):
        """Test getting an organization with proper permissions"""
        # Create test data
        user = User(email="test@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org_service = OrganizationService(db_session)
        org_data = OrganizationCreate(name="Test Org")
        organization = org_service.create_organization(org_data, user)
        
        # Get organization
        retrieved_org = org_service.get_organization(organization.id, user)
        
        assert retrieved_org.id == organization.id
        assert retrieved_org.name == "Test Org"
    
    def test_update_organization(self, db_session: Session):
        """Test updating an organization"""
        # Create test data
        user = User(email="test@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org_service = OrganizationService(db_session)
        org_data = OrganizationCreate(name="Original Name")
        organization = org_service.create_organization(org_data, user)
        
        # Update organization
        update_data = OrganizationUpdate(name="Updated Name")
        updated_org = org_service.update_organization(organization.id, update_data, user)
        
        assert updated_org.name == "Updated Name"
    
    def test_delete_organization(self, db_session: Session):
        """Test deleting an organization"""
        # Create test data
        user = User(email="test@example.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        org_service = OrganizationService(db_session)
        org_data = OrganizationCreate(name="To Delete")
        organization = org_service.create_organization(org_data, user)
        
        # Delete organization
        result = org_service.delete_organization(organization.id, user)
        
        assert result == True
        
        # Verify deletion
        deleted_org = db_session.query(Organization).filter(
            Organization.id == organization.id
        ).first()
        assert deleted_org is None
```