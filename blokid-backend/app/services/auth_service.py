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
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return access_token