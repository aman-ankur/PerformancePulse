"""
Team Management API endpoints
Handles team member CRUD operations and consent management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from ..api.auth import get_current_user
from ..services.database_service import DatabaseService  
from ..models import ProfileCreate, DataConsentCreate

router = APIRouter()
db_service = DatabaseService()

class TeamMemberCreate(BaseModel):
    full_name: str
    email: str
    gitlab_username: Optional[str] = None
    jira_username: Optional[str] = None

class TeamMemberResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    gitlab_username: Optional[str]
    jira_username: Optional[str]
    created_at: str

class ConsentUpdate(BaseModel):
    source_type: str  # 'gitlab', 'jira', or 'documents'
    consented: bool

class ConsentStatus(BaseModel):
    source_type: str
    consented: bool
    consented_at: Optional[str] = None

@router.get("/members", response_model=List[TeamMemberResponse])
async def get_team_members(current_user: dict = Depends(get_current_user)):
    """
    Get all team members for the authenticated manager
    """
    try:
        manager_id = UUID(current_user["id"])
        
        team_members = await db_service.get_team_members(manager_id)
        
        return [
            TeamMemberResponse(
                id=str(member.id),
                full_name=member.full_name,
                email=member.email,
                role=member.role,
                gitlab_username=member.gitlab_username,
                jira_username=member.jira_username,
                created_at=member.created_at.isoformat()
            )
            for member in team_members
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching team members: {str(e)}"
        )

@router.post("/members", response_model=TeamMemberResponse)
async def create_team_member(
    member_data: TeamMemberCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new team member
    """
    try:
        manager_id = UUID(current_user["id"])
        
        # Create profile data with manager relationship
        profile_data = ProfileCreate(
            full_name=member_data.full_name,
            email=member_data.email,
            role="team_member",
            manager_id=manager_id,
            gitlab_username=member_data.gitlab_username,
            jira_username=member_data.jira_username
        )
        
        # Generate a new UUID for team member - in real app this would come from OAuth
        from uuid import uuid4
        new_member_id = uuid4()
        
        profile = await db_service.create_profile(profile_data, new_member_id)
        
        # Create default consent records (all false initially)
        for source_type in ['gitlab', 'jira', 'documents']:
            consent_data = DataConsentCreate(
                team_member_id=profile.id,
                source_type=source_type,
                consented=False
            )
            await db_service.create_consent(consent_data)
        
        return TeamMemberResponse(
            id=str(profile.id),
            full_name=profile.full_name,
            email=profile.email,
            role=profile.role,
            gitlab_username=profile.gitlab_username,
            jira_username=profile.jira_username,
            created_at=profile.created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating team member: {str(e)}"
        )

@router.put("/members/{member_id}/consent")
async def update_consent(
    member_id: UUID,
    consent_data: ConsentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update data collection consent for a team member
    """
    try:
        manager_id = UUID(current_user["id"])
        
        # Verify manager has access to this team member
        from ..services.auth_service import AuthService
        auth_service = AuthService()
        
        has_access = await auth_service.verify_manager_access(manager_id, member_id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to manage this team member"
            )
        
        # Update consent
        updated_consent = await db_service.update_consent(
            member_id, 
            consent_data.source_type, 
            consent_data.consented
        )
        
        return {
            "message": "Consent updated successfully",
            "member_id": str(member_id),
            "source_type": consent_data.source_type,
            "consented": consent_data.consented,
            "updated_at": updated_consent.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating consent: {str(e)}"
        )

@router.get("/members/{member_id}/consent", response_model=List[ConsentStatus])
async def get_consent_status(
    member_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Get consent status for a team member
    """
    try:
        manager_id = UUID(current_user["id"])
        
        # Verify manager has access to this team member
        from ..services.auth_service import AuthService
        auth_service = AuthService()
        
        has_access = await auth_service.verify_manager_access(manager_id, member_id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this team member's consent"
            )
        
        consents = await db_service.get_consents(member_id)
        
        return [
            ConsentStatus(
                source_type=consent.source_type,
                consented=consent.consented,
                consented_at=consent.consented_at.isoformat() if consent.consented_at else None
            )
            for consent in consents
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching consent status: {str(e)}"
        ) 