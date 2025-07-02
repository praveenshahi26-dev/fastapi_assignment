from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token, User
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_active_user

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