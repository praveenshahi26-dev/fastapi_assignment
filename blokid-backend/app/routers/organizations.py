from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate, OrganizationInvite, OrganizationInviteResponse
from app.schemas.user import User
from app.services.organization_service import OrganizationService
from app.utils.dependencies import get_current_active_user, require_organization_admin, require_organization_access
from app.models.user import UserRole

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=Organization, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_create: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new organization"""
    org_service = OrganizationService(db)
    return org_service.create_organization(org_create, current_user)

@router.get("/", response_model=List[Organization])
def get_user_organizations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all organizations for current user"""
    org_service = OrganizationService(db)
    return org_service.get_user_organizations(current_user)

@router.get("/{organization_id}", response_model=Organization)
def get_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Manually check organization access
    require_organization_access(organization_id)(current_user, db)
    """Get specific organization"""
    org_service = OrganizationService(db)
    return org_service.get_organization(organization_id, current_user)

@router.put("/{organization_id}", response_model=Organization)
def update_organization(
    organization_id: int,
    org_update: OrganizationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Manually check organization access
    require_organization_access(organization_id)(current_user, db)
    """Update organization"""
    org_service = OrganizationService(db)
    return org_service.update_organization(organization_id, org_update, current_user)

@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Manually check organization admin access
    require_organization_admin(organization_id)(current_user, db)
    """Delete organization"""
    org_service = OrganizationService(db)
    org_service.delete_organization(organization_id, current_user)
    return None

@router.post("/{organization_id}/invite", response_model=OrganizationInviteResponse)
def invite_user_to_organization(
    organization_id: int,
    invite_data: OrganizationInvite,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Manually check organization admin access
    require_organization_admin(organization_id)(current_user, db)
    """Invite user to organization"""
    org_service = OrganizationService(db)
    membership = org_service.invite_user_to_organization(
        organization_id, 
        invite_data.email, 
        invite_data.role, 
        current_user
    )
    return {"message": "User invited successfully", "membership_id": membership.id}

@router.get("/{organization_id}/members")
def get_organization_members(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Manually check organization access
    require_organization_access(organization_id)(current_user, db)
    """Get organization members"""
    from app.models.user import OrganizationMember
    members = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id
    ).all()
    return [{"user_id": m.user_id, "role": m.role, "joined_at": m.created_at} for m in members]