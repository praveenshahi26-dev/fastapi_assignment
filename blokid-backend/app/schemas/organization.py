from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import User

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class OrganizationInDB(OrganizationBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Organization(OrganizationInDB):
    owner: Optional[User] = None
    # members: Optional[List[OrganizationMember]] = None

class OrganizationWithMembers(Organization):
    members: Optional[List['OrganizationMember']] = None

# Import after to avoid circular imports
from app.schemas.user import OrganizationMember
OrganizationWithMembers.model_rebuild()