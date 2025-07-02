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