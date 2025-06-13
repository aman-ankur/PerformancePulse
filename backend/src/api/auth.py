"""
Authentication API endpoints
Handles Google OAuth, session management, and user authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional

from ..services.auth_service import AuthService
from ..services.database_service import DatabaseService
from ..models import Profile

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
db_service = DatabaseService()

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    manager_id: Optional[str] = None

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current authenticated user"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        # Extract token from Bearer header
        token = authorization.replace("Bearer ", "")
        user_data = await auth_service.get_current_user(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return user_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    """
    try:
        from uuid import UUID
        user_id = UUID(current_user["id"])
        
        profile = await db_service.get_profile(user_id)
        
        if not profile:
            # Create profile if it doesn't exist
            profile = await auth_service.create_or_update_profile(current_user)
        
        return UserProfile(
            id=str(profile.id),
            email=profile.email,
            full_name=profile.full_name,
            role=profile.role,
            manager_id=str(profile.manager_id) if profile.manager_id else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user and invalidate token
    """
    try:
        # For now, just return success - actual token invalidation would depend on frontend
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging out: {str(e)}"
        )

@router.get("/health")
async def auth_health_check():
    """Health check for authentication service"""
    try:
        db_health = await db_service.health_check()
        
        return {
            "status": "healthy",
            "service": "auth",
            "database": db_health
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "auth",
            "error": str(e)
        } 