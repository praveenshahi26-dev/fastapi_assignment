from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.schemas.organization import Organization

class WebsiteBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None

class WebsiteCreate(WebsiteBase):
    organization_id: int

class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

class WebsiteInDB(WebsiteBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Website(WebsiteInDB):
    organization: Optional[Organization] = None

class WebsiteWithMembers(Website):
    members: Optional[List['WebsiteMember']] = None

# Import after to avoid circular imports
from app.schemas.user import WebsiteMember
WebsiteWithMembers.model_rebuild()