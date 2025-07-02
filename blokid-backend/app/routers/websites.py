from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.website import Website, WebsiteCreate, WebsiteUpdate, WebsiteInvite
from app.schemas.user import User
from app.services.website_service import WebsiteService
from app.utils.dependencies import (
    get_current_active_user, 
    require_website_admin, 
    require_website_access,
    require_organization_access
)

router = APIRouter(prefix="/websites", tags=["websites"])

@router.post("/", response_model=Website, status_code=status.HTTP_201_CREATED)
def create_website(
    website_create: WebsiteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new website"""
    website_service = WebsiteService(db)
    return website_service.create_website(website_create, current_user)

@router.get("/", response_model=List[Website])
def get_user_websites(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all websites for current user"""
    website_service = WebsiteService(db)
    return website_service.get_user_websites(current_user)

@router.get("/{website_id}", response_model=Website)
def get_website(
    website_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific website"""
    # Check access
    require_website_access(website_id)(current_user=current_user, db=db)
    website_service = WebsiteService(db)
    return website_service.get_website(website_id, current_user)

@router.put("/{website_id}", response_model=Website)
def update_website(
    website_id: int,
    website_update: WebsiteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update website"""
    # Check access
    require_website_access(website_id)(current_user=current_user, db=db)
    website_service = WebsiteService(db)
    return website_service.update_website(website_id, website_update, current_user)

@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_website(
    website_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete website"""
    # Check admin access
    require_website_admin(website_id)(current_user=current_user, db=db)
    website_service = WebsiteService(db)
    website_service.delete_website(website_id, current_user)
    return None

@router.post("/{website_id}/invite", status_code=status.HTTP_201_CREATED)
def invite_user_to_website(
    website_id: int,
    invite_data: WebsiteInvite,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Invite user to website"""
    # Check admin access
    require_website_admin(website_id)(current_user=current_user, db=db)
    website_service = WebsiteService(db)
    membership = website_service.invite_user_to_website(
        website_id=website_id,
        email=invite_data.email,
        role=invite_data.role,
        current_user=current_user
    )
    return {"message": "User invited successfully", "membership_id": membership.id}

@router.get("/{website_id}/members")
def get_website_members(
    website_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get website members"""
    # Check access
    require_website_access(website_id)(current_user=current_user, db=db)
    from app.models.user import WebsiteMember
    members = db.query(WebsiteMember).filter(
        WebsiteMember.website_id == website_id
    ).all()
    return [{"user_id": m.user_id, "role": m.role, "joined_at": m.created_at} for m in members]

@router.get("/organizations/{organization_id}/websites", response_model=List[Website])
def get_organization_websites(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all websites in an organization"""
    # Check organization access
    require_organization_access(organization_id)(current_user=current_user, db=db)
    website_service = WebsiteService(db)
    return website_service.get_organization_websites(organization_id, current_user)
