"""User/Profile models for PerformancePulse"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, UUID4, Field

RoleType = Literal["team_member", "manager"]

class ProfileBase(BaseModel):
    """Base profile model with common fields"""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: RoleType = "team_member"
    gitlab_username: Optional[str] = None
    jira_username: Optional[str] = None

class ProfileCreate(ProfileBase):
    """Model for creating a new profile"""
    manager_id: Optional[UUID4] = None

class ProfileUpdate(BaseModel):
    """Model for updating an existing profile"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    gitlab_username: Optional[str] = None
    jira_username: Optional[str] = None

class Profile(ProfileBase):
    """Complete profile model with database fields"""
    id: UUID4
    manager_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 