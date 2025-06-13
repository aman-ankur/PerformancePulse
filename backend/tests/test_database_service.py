"""
Test suite for DatabaseService
Tests all database operations with proper mocking for MVP
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import datetime, date

from src.services.database_service import DatabaseService
from src.models import (
    Profile, ProfileCreate, ProfileUpdate,
    EvidenceItem, EvidenceItemCreate,
    DataConsent, DataConsentCreate
)

@pytest.fixture
def db_service():
    """Create DatabaseService instance with mocked client"""
    with patch('src.services.database_service.get_supabase_client') as mock_client:
        service = DatabaseService()
        service.client = Mock()
        return service, service.client

@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing"""
    return {
        "id": str(uuid4()),
        "full_name": "Test Manager",
        "email": "manager@test.com",
        "role": "manager",
        "gitlab_username": "test_manager",
        "jira_username": "test.manager",
        "manager_id": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def sample_team_member_data():
    """Sample team member data for testing"""
    manager_id = uuid4()
    return {
        "id": str(uuid4()),
        "full_name": "Test Developer",
        "email": "dev@test.com",
        "role": "team_member",
        "gitlab_username": "test_dev",
        "jira_username": "test.dev",
        "manager_id": str(manager_id),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

class TestProfileOperations:
    """Test profile/user management operations"""
    
    @pytest.mark.asyncio
    async def test_create_profile_success(self, db_service):
        service, mock_client = db_service
        
        # Mock successful database response
        mock_client.table().insert().execute.return_value = Mock(
            data=[{
                "id": str(uuid4()),
                "full_name": "Test User",
                "email": "test@example.com",
                "role": "manager",
                "gitlab_username": None,
                "jira_username": None,
                "manager_id": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }]
        )
        
        profile_data = ProfileCreate(
            full_name="Test User",
            email="test@example.com",
            role="manager"
        )
        
        result = await service.create_profile(profile_data, uuid4())
        
        assert isinstance(result, Profile)
        assert result.full_name == "Test User"
        assert result.email == "test@example.com"
        assert result.role == "manager"
    
    @pytest.mark.asyncio
    async def test_get_profile_exists(self, db_service, sample_profile_data):
        service, mock_client = db_service
        
        # Mock profile exists
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[sample_profile_data]
        )
        
        user_id = UUID(sample_profile_data["id"])
        result = await service.get_profile(user_id)
        
        assert result is not None
        assert result.email == sample_profile_data["email"]
        assert result.full_name == sample_profile_data["full_name"]
    
    @pytest.mark.asyncio
    async def test_get_profile_not_exists(self, db_service):
        service, mock_client = db_service
        
        # Mock profile doesn't exist
        mock_client.table().select().eq().execute.return_value = Mock(data=[])
        
        result = await service.get_profile(uuid4())
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_team_members(self, db_service, sample_team_member_data):
        service, mock_client = db_service
        
        # Mock team members response
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[sample_team_member_data]
        )
        
        manager_id = uuid4()
        result = await service.get_team_members(manager_id)
        
        assert len(result) == 1
        assert result[0].role == "team_member"
        assert result[0].manager_id == UUID(sample_team_member_data["manager_id"])

class TestEvidenceOperations:
    """Test evidence management operations"""
    
    @pytest.mark.asyncio
    async def test_create_evidence_with_consent(self, db_service):
        service, mock_client = db_service
        
        # Mock consent check returns True
        with patch.object(service, '_check_consent', return_value=True):
            # Mock successful evidence creation
            mock_client.table().insert().execute.return_value = Mock(
                data=[{
                    "id": str(uuid4()),
                    "team_member_id": str(uuid4()),
                    "source": "gitlab_commit",
                    "title": "Fix authentication bug",
                    "description": "Resolved OAuth flow issue",
                    "category": "technical",
                    "evidence_date": date.today().isoformat(),
                    "source_url": "https://gitlab.com/repo/commit/abc123",
                    "metadata": {},
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }]
            )
            
            evidence_data = EvidenceItemCreate(
                team_member_id=uuid4(),
                source="gitlab_commit",
                title="Fix authentication bug",
                description="Resolved OAuth flow issue",
                evidence_date=date.today(),
                source_url="https://gitlab.com/repo/commit/abc123"
            )
            
            result = await service.create_evidence_item(evidence_data)
            
            assert isinstance(result, EvidenceItem)
            assert result.source == "gitlab_commit"
            assert result.title == "Fix authentication bug"
    
    @pytest.mark.asyncio
    async def test_create_evidence_without_consent(self, db_service):
        service, mock_client = db_service
        
        # Mock consent check returns False
        with patch.object(service, '_check_consent', return_value=False):
            evidence_data = EvidenceItemCreate(
                team_member_id=uuid4(),
                source="gitlab_commit",
                title="Test commit",
                description="Test description",
                evidence_date=date.today()
            )
            
            with pytest.raises(PermissionError, match="No consent"):
                await service.create_evidence_item(evidence_data)
    
    @pytest.mark.asyncio
    async def test_get_evidence_items(self, db_service):
        service, mock_client = db_service
        
        # Mock evidence items response
        mock_client.table().select().eq().order().limit().execute.return_value = Mock(
            data=[{
                "id": str(uuid4()),
                "team_member_id": str(uuid4()),
                "source": "gitlab_commit",
                "title": "Test commit",
                "description": "Test description",
                "category": "technical",
                "evidence_date": date.today().isoformat(),
                "source_url": None,
                "metadata": {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }]
        )
        
        result = await service.get_evidence_items(uuid4())
        
        assert len(result) == 1
        assert result[0].source == "gitlab_commit"

class TestConsentOperations:
    """Test consent management operations"""
    
    @pytest.mark.asyncio
    async def test_create_consent(self, db_service):
        service, mock_client = db_service
        
        # Mock successful consent creation
        mock_client.table().upsert().execute.return_value = Mock(
            data=[{
                "id": str(uuid4()),
                "team_member_id": str(uuid4()),
                "source_type": "gitlab",
                "consented": True,
                "consented_at": datetime.utcnow().isoformat(),
                "revoked_at": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }]
        )
        
        consent_data = DataConsentCreate(
            team_member_id=uuid4(),
            source_type="gitlab",
            consented=True
        )
        
        result = await service.create_consent(consent_data)
        
        assert isinstance(result, DataConsent)
        assert result.source_type == "gitlab"
        assert result.consented is True
    
    @pytest.mark.asyncio
    async def test_check_consent_exists(self, db_service):
        service, mock_client = db_service
        
        # Mock consent exists and is granted
        mock_client.table().select().eq().eq().execute.return_value = Mock(
            data=[{"consented": True}]
        )
        
        result = await service._check_consent(uuid4(), "gitlab")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_consent_not_exists(self, db_service):
        service, mock_client = db_service
        
        # Mock no consent record
        mock_client.table().select().eq().eq().execute.return_value = Mock(data=[])
        
        result = await service._check_consent(uuid4(), "gitlab")
        assert result is False
    
    def test_source_to_consent_type_mapping(self, db_service):
        service, _ = db_service
        
        assert service._source_to_consent_type("gitlab_commit") == "gitlab"
        assert service._source_to_consent_type("gitlab_mr") == "gitlab"
        assert service._source_to_consent_type("jira_ticket") == "jira"
        assert service._source_to_consent_type("document") == "documents"
        
        with pytest.raises(ValueError):
            service._source_to_consent_type("unknown_source")

class TestHealthCheck:
    """Test health check functionality"""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, db_service):
        service, mock_client = db_service
        
        # Mock successful health check
        mock_client.table().select().limit().execute.return_value = Mock(data=[])
        
        result = await service.health_check()
        
        assert result["status"] == "healthy"
        assert result["database"] == "connected"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, db_service):
        service, mock_client = db_service
        
        # Mock database connection failure
        mock_client.table().select().limit().execute.side_effect = Exception("Connection failed")
        
        result = await service.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["database"] == "disconnected"
        assert "error" in result
        assert "timestamp" in result 