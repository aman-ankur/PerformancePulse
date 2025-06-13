"""Data consent models for PerformancePulse"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, UUID4

ConsentSourceType = Literal["gitlab", "jira", "documents"]

class DataConsentBase(BaseModel):
    """Base data consent model with common fields"""
    source_type: ConsentSourceType
    consented: bool = False

class DataConsentCreate(DataConsentBase):
    """Model for creating a new data consent"""
    team_member_id: UUID4

class DataConsentUpdate(BaseModel):
    """Model for updating an existing data consent"""
    consented: Optional[bool] = None

class DataConsent(DataConsentBase):
    """Complete data consent model with database fields"""
    id: UUID4
    team_member_id: UUID4
    consented_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 