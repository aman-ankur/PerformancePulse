"""
Authentication service for PerformancePulse
Handles Google OAuth, session management, and user context
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID

from ..database.connection import get_supabase_client
from ..models import Profile, ProfileCreate

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication and user session management"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def get_current_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get current user from access token"""
        try:
            # Use Supabase to verify the token and get user
            user_response = self.client.auth.get_user(access_token)
            
            if user_response.user:
                return {
                    "id": user_response.user.id,
                    "email": user_response.user.email,
                    "user_metadata": user_response.user.user_metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None
    
    async def create_or_update_profile(self, user_data: Dict[str, Any]) -> Profile:
        """Create or update user profile after OAuth"""
        try:
            from ..services.database_service import DatabaseService
            db_service = DatabaseService()
            
            user_id = UUID(user_data["id"])
            
            # Check if profile exists
            existing_profile = await db_service.get_profile(user_id)
            
            if existing_profile:
                return existing_profile
            
            # Create new profile
            profile_data = ProfileCreate(
                full_name=user_data.get("user_metadata", {}).get("full_name", user_data["email"]),
                email=user_data["email"],
                role="manager"  # Default to manager for MVP
            )
            
            return await db_service.create_profile(profile_data, user_id)
            
        except Exception as e:
            logger.error(f"Error creating/updating profile: {str(e)}")
            raise
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out user"""
        try:
            self.client.auth.sign_out()
            return True
            
        except Exception as e:
            logger.error(f"Error signing out user: {str(e)}")
            return False
    
    async def verify_manager_access(self, user_id: UUID, team_member_id: UUID) -> bool:
        """Verify if user is manager of the team member"""
        try:
            from ..services.database_service import DatabaseService
            db_service = DatabaseService()
            
            team_member = await db_service.get_profile(team_member_id)
            
            if not team_member:
                return False
            
            return str(team_member.manager_id) == str(user_id)
            
        except Exception as e:
            logger.error(f"Error verifying manager access: {str(e)}")
            return False 