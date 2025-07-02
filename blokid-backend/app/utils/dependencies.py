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