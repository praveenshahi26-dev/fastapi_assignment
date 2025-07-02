from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.website import Website, WebsiteMember
from app.schemas.website import Website, WebsiteCreate, WebsiteUpdate, WebsiteMemberCreate
from app.services.permission_service import PermissionService

router = APIRouter()

@router.post("/", response_model=Website)
async def create_website(
    website_create: WebsiteCreate,
    db: Session = Depends(get_db)
):
    db_website = Website(**website_create.model_dump())
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

@router.get("/", response_model=List[Website])
async def get_websites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    websites = db.query(Website).offset(skip).limit(limit).all()
    return websites

@router.get("/{website_id}", response_model=Website)
async def get_website(
    website_id: int,
    db: Session = Depends(get_db)
):
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    return website

@router.post("/{website_id}/members", response_model=WebsiteMember)
async def add_website_member(
    website_id: int,
    member_create: WebsiteMemberCreate,
    db: Session = Depends(get_db)
):
    permission_service = PermissionService(db)
    
    # Check if user has permission to add members
    if not permission_service.can_manage_website(
        user_id=member_create.user_id,
        website_id=website_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add members"
        )
    
    member = WebsiteMember(**member_create.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
