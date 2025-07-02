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