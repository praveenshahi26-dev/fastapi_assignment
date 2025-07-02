from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class OrganizationMemberBase(BaseModel):
    user_id: int
    organization_id: int
    role: UserRole

class OrganizationMemberCreate(OrganizationMemberBase):
    pass

class OrganizationMember(OrganizationMemberBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WebsiteMemberBase(BaseModel):
    user_id: int
    website_id: int
    role: UserRole

class WebsiteMemberCreate(WebsiteMemberBase):
    pass

class WebsiteMember(WebsiteMemberBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True