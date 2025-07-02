from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.website import Website
from app.models.user import User, WebsiteMember, UserRole
from app.schemas.website import WebsiteCreate, WebsiteUpdate
from app.services.permission_service import PermissionService
from typing import List

class WebsiteService:
    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)
    
    def create_website(self, website_create: WebsiteCreate, user: User) -> Website:
        """Create a new website"""
        if not self.permission_service.can_create_website_in_organization(
            user, website_create.organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create websites in this organization"
            )
        
        website = Website(
            name=website_create.name,
            description=website_create.description,
            url=website_create.url,
            organization_id=website_create.organization_id
        )
        self.db.add(website)
        self.db.commit()
        self.db.refresh(website)
        
        # Add creator as website admin if they're not org admin
        if not self.permission_service.can_manage_organization(user, website_create.organization_id):
            membership = WebsiteMember(
                user_id=user.id,
                website_id=website.id,
                role=UserRole.WEBSITE_ADMIN
            )
            self.db.add(membership)
            self.db.commit()
        
        return website
    
    def get_website(self, website_id: int, user: User) -> Website:
        """Get a website by ID"""
        if not self.permission_service.can_read_website(user, website_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this website"
            )
        
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Website not found"
            )
        
        return website
    
    def get_organization_websites(self, organization_id: int, user: User) -> List[Website]:
        """Get all websites in an organization"""
        if not self.permission_service.can_read_organization(user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this organization"
            )
        
        return self.db.query(Website).filter(
            Website.organization_id == organization_id
        ).all()
    
    def get_user_websites(self, user: User) -> List[Website]:
        """Get all websites for a user"""
        return self.permission_service.get_user_websites(user)
    
    def update_website(
        self, 
        website_id: int, 
        website_update: WebsiteUpdate, 
        user: User
    ) -> Website:
        """Update a website"""
        if not self.permission_service.can_update_website(user, website_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this website"
            )
        
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Website not found"
            )
        
        # Update fields
        update_data = website_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(website, field, value)
        
        self.db.commit()
        self.db.refresh(website)
        
        return website
    
    def delete_website(self, website_id: int, user: User) -> bool:
        """Delete a website"""
        if not self.permission_service.can_manage_website(user, website_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this website"
            )
        
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Website not found"
            )
        
        # Delete associated memberships first
        self.db.query(WebsiteMember).filter(
            WebsiteMember.website_id == website_id
        ).delete()
        
        # Delete website
        self.db.delete(website)
        self.db.commit()
        
        return True
    
    def invite_user_to_website(
        self, 
        website_id: int, 
        user_email: str, 
        role: UserRole, 
        inviter: User
    ) -> WebsiteMember:
        """Invite a user to a website"""
        if not self.permission_service.can_manage_website(inviter, website_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to invite users to this website"
            )
        
        # Find user to invite
        user_to_invite = self.db.query(User).filter(User.email == user_email).first()
        if not user_to_invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is already a member
        existing_membership = self.db.query(WebsiteMember).filter(
            WebsiteMember.user_id == user_to_invite.id,
            WebsiteMember.website_id == website_id
        ).first()
        
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this website"
            )
        
        # Create membership
        membership = WebsiteMember(
            user_id=user_to_invite.id,
            website_id=website_id,
            role=role
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        
        return membership