"""
Database service layer for PerformancePulse
Handles all database operations with proper error handling and consent checking
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..database.connection import get_supabase_client  
from ..models import (
    Profile, ProfileCreate, ProfileUpdate,
    EvidenceItem, EvidenceItemCreate, EvidenceItemUpdate,
    DataConsent, DataConsentCreate, DataConsentUpdate
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service layer for database operations with consent and RLS enforcement"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    # Profile/User Management
    async def create_profile(self, profile_data: ProfileCreate, user_id: UUID) -> Profile:
        """Create a new user profile"""
        try:
            # Prepare data for insertion
            data = profile_data.model_dump(exclude_unset=True)
            data['id'] = str(user_id)
            
            result = self.client.table('profiles').insert(data).execute()
            
            if not result.data:
                raise ValueError("Failed to create profile")
            
            return Profile(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            raise
    
    async def get_profile(self, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID"""
        try:
            result = self.client.table('profiles').select('*').eq('id', str(user_id)).execute()
            
            if result.data:
                return Profile(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error fetching profile {user_id}: {str(e)}")
            raise
    
    async def get_team_members(self, manager_id: UUID) -> List[Profile]:
        """Get all team members for a manager"""
        try:
            result = self.client.table('profiles').select('*').eq('manager_id', str(manager_id)).execute()
            
            return [Profile(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching team members for {manager_id}: {str(e)}")
            raise
    
    async def update_profile(self, user_id: UUID, profile_data: ProfileUpdate) -> Profile:
        """Update user profile"""
        try:
            data = profile_data.model_dump(exclude_unset=True, exclude_none=True)
            
            if not data:
                # No changes to make
                return await self.get_profile(user_id)
            
            result = self.client.table('profiles').update(data).eq('id', str(user_id)).execute()
            
            if not result.data:
                raise ValueError("Failed to update profile")
            
            return Profile(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error updating profile {user_id}: {str(e)}")
            raise
    
    # Evidence Management
    async def create_evidence_item(self, evidence_data: EvidenceItemCreate) -> EvidenceItem:
        """Create a new evidence item"""
        try:
            # Check consent before creating evidence
            has_consent = await self._check_consent(
                evidence_data.team_member_id, 
                self._source_to_consent_type(evidence_data.source)
            )
            
            if not has_consent:
                raise PermissionError(f"No consent for {evidence_data.source} data collection")
            
            data = evidence_data.model_dump(exclude_unset=True)
            data['team_member_id'] = str(data['team_member_id'])
            
            result = self.client.table('evidence_items').insert(data).execute()
            
            if not result.data:
                raise ValueError("Failed to create evidence item")
            
            return EvidenceItem(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating evidence item: {str(e)}")
            raise
    
    async def get_evidence_items(self, team_member_id: UUID, limit: int = 100) -> List[EvidenceItem]:
        """Get evidence items for a team member"""
        try:
            result = (self.client.table('evidence_items')
                     .select('*')
                     .eq('team_member_id', str(team_member_id))
                     .order('evidence_date', desc=True)
                     .limit(limit)
                     .execute())
            
            return [EvidenceItem(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching evidence for {team_member_id}: {str(e)}")
            raise
    
    async def get_team_evidence(self, manager_id: UUID, days: int = 30) -> List[EvidenceItem]:
        """Get all evidence for a manager's team members"""
        try:
            # Get team member IDs first
            team_members = await self.get_team_members(manager_id)
            team_member_ids = [str(member.id) for member in team_members]
            
            if not team_member_ids:
                return []
            
            result = (self.client.table('evidence_items')
                     .select('*')
                     .in_('team_member_id', team_member_ids)
                     .order('evidence_date', desc=True)
                     .execute())
            
            return [EvidenceItem(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching team evidence for {manager_id}: {str(e)}")
            raise
    
    # Consent Management
    async def create_consent(self, consent_data: DataConsentCreate) -> DataConsent:
        """Create or update data consent"""
        try:
            data = consent_data.model_dump(exclude_unset=True)
            data['team_member_id'] = str(data['team_member_id'])
            
            if data['consented']:
                data['consented_at'] = datetime.utcnow().isoformat()
                data['revoked_at'] = None
            else:
                data['revoked_at'] = datetime.utcnow().isoformat()
            
            # Use upsert to handle existing consents
            result = (self.client.table('data_consents')
                     .upsert(data, on_conflict='team_member_id,source_type')
                     .execute())
            
            if not result.data:
                raise ValueError("Failed to create consent")
            
            return DataConsent(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating consent: {str(e)}")
            raise
    
    async def get_consents(self, team_member_id: UUID) -> List[DataConsent]:
        """Get all consents for a team member"""
        try:
            result = (self.client.table('data_consents')
                     .select('*')
                     .eq('team_member_id', str(team_member_id))
                     .execute())
            
            return [DataConsent(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching consents for {team_member_id}: {str(e)}")
            raise
    
    async def update_consent(self, team_member_id: UUID, source_type: str, consented: bool) -> DataConsent:
        """Update consent status"""
        try:
            data = {
                'consented': consented,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if consented:
                data['consented_at'] = datetime.utcnow().isoformat()
                data['revoked_at'] = None
            else:
                data['revoked_at'] = datetime.utcnow().isoformat()
            
            result = (self.client.table('data_consents')
                     .update(data)
                     .eq('team_member_id', str(team_member_id))
                     .eq('source_type', source_type)
                     .execute())
            
            if not result.data:
                raise ValueError("Failed to update consent")
            
            return DataConsent(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error updating consent: {str(e)}")
            raise
    
    # Helper Methods
    async def _check_consent(self, team_member_id: UUID, source_type: str) -> bool:
        """Check if team member has consented to data collection"""
        try:
            result = (self.client.table('data_consents')
                     .select('consented')
                     .eq('team_member_id', str(team_member_id))
                     .eq('source_type', source_type)
                     .execute())
            
            if result.data:
                return result.data[0]['consented']
            
            # No consent record means no consent
            return False
            
        except Exception as e:
            logger.error(f"Error checking consent: {str(e)}")
            return False
    
    def _source_to_consent_type(self, source: str) -> str:
        """Map evidence source to consent type"""
        if source.startswith('gitlab'):
            return 'gitlab'
        elif source.startswith('jira'):
            return 'jira'
        elif source == 'document':
            return 'documents'
        else:
            raise ValueError(f"Unknown source type: {source}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            # Test basic connectivity
            result = self.client.table('profiles').select('count').limit(1).execute()
            
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy", 
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 