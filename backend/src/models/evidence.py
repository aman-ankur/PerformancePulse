"""Evidence models for PerformancePulse"""

from typing import Optional, Literal, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, UUID4, Field, HttpUrl

SourceType = Literal["gitlab_commit", "gitlab_mr", "jira_ticket", "document"]
CategoryType = Literal["technical", "collaboration", "delivery"]

class EvidenceItemBase(BaseModel):
    """Base evidence item model with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    source: SourceType
    category: CategoryType = "technical"
    evidence_date: date
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Author context (optional)
    author_name: Optional[str] = None
    author_email: Optional[str] = None

class EvidenceItemCreate(EvidenceItemBase):
    """Model for creating a new evidence item"""
    team_member_id: UUID4

class EvidenceItemUpdate(BaseModel):
    """Model for updating an existing evidence item"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[CategoryType] = None
    evidence_date: Optional[date] = None
    source_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    author_name: Optional[str] = None
    author_email: Optional[str] = None

class EvidenceItem(EvidenceItemBase):
    """Complete evidence item model with database fields"""
    id: UUID4
    team_member_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 