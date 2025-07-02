from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.organization import Organization, OrganizationMember
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate, OrganizationMemberCreate
from app.services.permission_service import PermissionService

router = APIRouter()

@router.post("/", response_model=Organization)
async def create_organization(
    org_create: OrganizationCreate,
    db: Session = Depends(get_db)
):
    db_org = Organization(**org_create.model_dump())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

@router.get("/", response_model=List[Organization])
async def get_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations

@router.get("/{org_id}", response_model=Organization)
async def get_organization(
    org_id: int,
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return org

@router.post("/{org_id}/members", response_model=OrganizationMember)
async def add_organization_member(
    org_id: int,
    member_create: OrganizationMemberCreate,
    db: Session = Depends(get_db)
):
    permission_service = PermissionService(db)
    
    # Check if user has permission to add members
    if not permission_service.can_manage_organization(
        user_id=member_create.user_id,
        organization_id=org_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add members"
        )
    
    member = OrganizationMember(**member_create.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
