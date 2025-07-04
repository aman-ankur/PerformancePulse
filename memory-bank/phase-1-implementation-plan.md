# PerformancePulse - Phase 1 Implementation Plan
## Core Data Pipeline & MVP Foundation

**Philosophy: "Test-First, MVP-Focused, Manager-Centric + SIMPLIFIED FOR PERSONAL/TEAM USE"**

Build a solid, testable foundation that solves the core problem: collecting and organizing engineering evidence for manager-team member conversations. Focus on essential features that provide immediate value while maintaining high code quality and comprehensive test coverage.

**⚡ SIMPLIFIED APPROACH FOR PERSONAL/TEAM USE:**
- **Consent Management**: Simple on/off toggles instead of granular controls
- **Team Assumption**: Team members have agreed to share data (minimal friction)
- **Manager-Focused**: Optimized for personal use and small teams
- **Data-First**: Prioritize evidence collection over privacy complexity
- **Streamlined UX**: Minimal setup, maximum value

**🚀 MCP-FIRST HYBRID APPROACH - PHASE 1.2.1 COMPLETE:**
- **Primary Method**: MCP (Model Context Protocol) integration for GitLab and JIRA
- **Fallback Method**: Direct API calls when MCP is unavailable
- **Benefits**: Leverage proven MCP tools with reliability of API fallback
- **Status**: GitLab MCP integration ✅ COMPLETE, JIRA integration 🔄 NEXT

**📊 CURRENT PROGRESS:**
- ✅ **Phase 1.1**: Foundation & Authentication (Complete)
- ✅ **Phase 1.2.1**: GitLab MCP Integration (Complete)
- ✅ **Phase 1.2.2**: JIRA MCP Integration (Complete)
- 🚧 **Phase 1.2.3**: Cross-Platform Correlation Engine (In Progress)
- ⏳ **Phase 1.3**: Document Processing (Planned)
- ✅ **Phase 1.4.1**: FastAPI Backend Setup (Complete)

---

## 3-4 Phase Project Overview

### Phase 1 (Weeks 1-2): Core Data Pipeline & MVP Foundation
- **Goal**: Collect and organize evidence from GitLab/Jira using MCP-first hybrid approach
- **Output**: Managers can collect evidence with consent and view organized contributions

### Phase 2 (Weeks 3-4): AI Analysis & Meeting Preparation
- **Goal**: Add Claude AI for evidence correlation and meeting preparation generation
- **Output**: Generate structured meeting prep in 30 minutes vs 3 days

### Phase 3 (Weeks 5-6): Production Polish & Advanced Features  
- **Goal**: Production-ready with exports, privacy controls, and performance optimization
- **Output**: Deployable tool with excellent UX and privacy compliance

### Phase 4 (Future): Scale & Enhancement
- **Goal**: Advanced analytics, team insights, and additional integrations
- **Output**: Enterprise-ready platform with comprehensive manager workflows

---

## Phase 1: Core Data Pipeline (Weeks 1-2)

### Phase 1.1: Project Foundation & Authentication (Days 1-3) ✅ COMPLETE
**Goal**: Establish robust project structure with secure authentication

#### 1.1.1: Development Environment Setup (Day 1) ✅ COMPLETE
**Tasks:**
- [x] Create monorepo structure with `frontend/` and `backend/` directories
- [x] Initialize Next.js 14 with App Router + TypeScript (strict mode) in `frontend/`
- [x] Configure Tailwind CSS + Shadcn/ui with manager-focused theme
- [x] Set up FastAPI project structure in `backend/src/`
- [x] Set up ESLint + Prettier + Husky for code quality
- [x] Initialize Git repository with proper .gitignore for both environments
- [x] Configure environment variables structure for both frontend and backend
- [x] Create Docker Compose for development environment
- [x] Set up shared types directory for TypeScript definitions

**Testing Strategy:**
```bash
# Development tooling tests
npm run lint        # ESLint checks
npm run type-check  # TypeScript compilation
npm run test:setup  # Environment configuration validation
```

**Acceptance Criteria:**
- [x] TypeScript compiles without errors in strict mode
- [x] All linting rules pass
- [x] Environment variables load correctly
- [x] Git hooks prevent commits with lint errors

#### 1.1.2: Database Schema & Supabase Setup (Day 1-2) ✅ COMPLETE
**Tasks:**
- [x] Create Supabase project with PostgreSQL database
- [x] Implement core schema: `profiles`, `team_members`, `evidence_items`
- [x] Set up Row Level Security (RLS) policies for team isolation
- [x] Configure Google OAuth for manager authentication
- [x] Enable real-time subscriptions for team data

**Database Schema (MVP Focus):**
```sql
-- Core manager-team relationship
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  role TEXT DEFAULT 'team_member' CHECK (role IN ('team_member', 'manager')),
  manager_id UUID REFERENCES profiles(id),
  gitlab_username TEXT,
  jira_username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evidence collection with consent
CREATE TABLE evidence_items (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('gitlab_commit', 'gitlab_mr', 'jira_ticket')),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  source_url TEXT,
  category TEXT DEFAULT 'technical' CHECK (category IN ('technical', 'collaboration', 'delivery')),
  evidence_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Consent tracking
CREATE TABLE data_consents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN ('gitlab', 'jira')),
  consented BOOLEAN DEFAULT FALSE,
  consented_at TIMESTAMP WITH TIME ZONE,
  revoked_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(team_member_id, source_type)
);
```

**Testing Strategy:**
```typescript
// Database schema tests
describe('Database Schema', () => {
  it('should create all tables with correct constraints', async () => {
    // Test table creation and constraints
  })
  
  it('should enforce RLS policies for team isolation', async () => {
    // Test that managers only see their team data
  })
  
  it('should handle consent tracking correctly', async () => {
    // Test consent grant/revoke workflows
  })
})
```

**Acceptance Criteria:**
- [x] All database tables created with proper constraints
- [x] RLS policies prevent unauthorized data access
- [x] Google OAuth authentication works
- [x] Real-time subscriptions update correctly

#### 1.1.3: Authentication & Team Management UI (Day 2-3) ✅ COMPLETE
**Tasks:**
- [x] **Google OAuth Implementation**: Complete end-to-end OAuth flow
  - [x] Google OAuth provider configured in Supabase dashboard
  - [x] Client ID and Client Secret properly set up
  - [x] PKCE (Proof Key for Code Exchange) flow implementation
  - [x] Automatic profile creation for new OAuth users
- [x] **Auth State Management**: Comprehensive Zustand-based authentication
  - [x] Session management with automatic initialization
  - [x] Real-time auth state listeners (SIGNED_IN, SIGNED_OUT, TOKEN_REFRESHED)
  - [x] Enhanced error handling and recovery mechanisms
  - [x] Persistent state with security considerations
- [x] **Team Management Interface**: Complete UI for team member management
  - [x] Team member list with consent status indicators
  - [x] Add member dialog with form validation
  - [x] Consent management dialog with granular controls
  - [x] Privacy-first design with clear explanations
- [x] **Manager Dashboard**: Full-featured dashboard interface
  - [x] Welcome personalization with user data
  - [x] Statistics cards for team metrics
  - [x] Quick action buttons for core workflows
  - [x] Sign out functionality

**Key Components:**
```typescript
// Auth service with comprehensive error handling ✅ IMPLEMENTED
export class AuthService {
  async signInWithGoogle(): Promise<AuthResult>
  async signOut(): Promise<void>
  async getCurrentUser(): Promise<User | null>
  async refreshToken(): Promise<void>
}

// Team management with consent tracking ✅ IMPLEMENTED
export class TeamService {
  async addTeamMember(data: TeamMemberData): Promise<TeamMember>
  async getTeamMembers(managerId: string): Promise<TeamMember[]>
  async updateConsent(memberId: string, source: string, consented: boolean): Promise<void>
}
```

**Testing Strategy:**
```typescript
// Authentication tests ✅ 31/31 TESTS PASSING
describe('AuthService', () => {
  it('should authenticate manager with Google OAuth', async () => {
    // Mock Google OAuth flow
  })
  
  it('should handle authentication failures gracefully', async () => {
    // Test error scenarios
  })
  
  it('should maintain auth state correctly', async () => {
    // Test state persistence
  })
})

// Team management tests ✅ IMPLEMENTED
describe('TeamService', () => {
  it('should add team member with proper validation', async () => {
    // Test team member creation
  })
  
  it('should enforce manager-only team management', async () => {
    // Test authorization
  })
})
```

**Acceptance Criteria:**
- [x] **OAuth Flow**: Managers can authenticate with Google OAuth completely
- [x] **Profile Creation**: New OAuth users automatically get manager profiles
- [x] **Team Management**: Team members can be added/managed by their manager only
- [x] **Consent Tracking**: Consent status is tracked and displayed correctly
- [x] **Session Persistence**: Authentication state persists across browser sessions
- [x] **Real Database**: All operations work with live Supabase database
- [x] **Production Build**: Clean code with no debug logs, optimized build
- [x] **Test Coverage**: 31/31 tests passing with comprehensive coverage

**🎉 MAJOR MILESTONE ACHIEVED:**
- ✅ **Google OAuth**: Complete end-to-end authentication working
- ✅ **Database Integration**: Real Supabase integration with proper RLS policies
- ✅ **UI Components**: Full team management interface
- ✅ **Error Handling**: Robust error recovery and user feedback
- ✅ **Production Ready**: Clean, optimized, and well-tested codebase

---

### Phase 1.2: Data Collection Pipeline - MCP-FIRST HYBRID APPROACH 🚀 (Days 4-7)
**Goal**: Implement robust data collection using MCP servers with API fallback

**🎯 CONFIRMED WORKING: GitLab MCP Integration Successfully Tested**
- ✅ GitLab MCP server (@zereight/mcp-gitlab) confirmed working
- ✅ User activity detection confirmed (test user successful)
- ✅ Project access verified (test project access working)
- ✅ Merge requests and commit data retrieval working
- ✅ Ready for production implementation

#### 1.2.1: GitLab MCP Integration (Day 4-5) ✅ **COMPLETE**
**Tasks:**
- [x] **MCP Server Setup**: Configure GitLab MCP server with proper environment
- [x] **Connection Testing**: Verify MCP server communication via stdio
- [x] **User Activity Testing**: Confirm user commit/MR retrieval
- [x] **Backend Integration**: Implement GitLab MCP client in FastAPI
- [x] **API Fallback**: Implement direct GitLab API as backup method
- [x] **Hybrid Logic**: Smart switching between MCP and API based on availability
- [x] **Security Cleanup**: Remove sensitive data, add configuration templates
- [x] **Documentation**: Complete MCP architecture documentation
- [x] **Testing**: Comprehensive test suite with successful verification
- [x] **FastAPI Endpoints**: Evidence collection API endpoints implemented
- [x] **Data Models**: EvidenceItem and related Pydantic models
- [x] **Production Ready**: Environment-based configuration, no hardcoded secrets

**GitLab MCP-First Implementation (Python/FastAPI):**
```python
class GitLabHybridClient:
    """GitLab MCP-first hybrid client with API fallback"""
    
    def __init__(self, gitlab_token: str, project_id: str, gitlab_url: str = "https://gitlab.com/api/v4"):
        self.mcp_client = GitLabMCPClient(gitlab_token, gitlab_url)
        self.api_client = GitLabAPIClient(gitlab_token, gitlab_url)
        self.project_id = project_id
    
    async def check_mcp_health(self) -> bool:
        """Check if MCP server is available"""
        try:
            response = await self.mcp_client.list_tools()
            return response.success
        except Exception:
            return False
    
    async def get_merge_requests(self, username: str, since_date: datetime) -> List[EvidenceItem]:
        """Get merge requests with MCP-first approach"""
        try:
            # Try MCP first (preferred method)
            mcp_response = await self.mcp_client.get_merge_requests(
                self.project_id, username, since_date
            )
            if mcp_response.success:
                return self._transform_mcp_merge_requests(
                    mcp_response.data, username, DataSource.MCP, False
                )
        except Exception as e:
            logger.warning(f'MCP failed, falling back to API: {e}')
        
        # Fallback to direct API
        api_data = await self.api_client.get_merge_requests(
            self.project_id, username, since_date
        )
        return self._transform_api_merge_requests(
            api_data, username, DataSource.API, True
        )
    
    async def get_comprehensive_evidence(self, username: str, days_back: int = 7) -> List[EvidenceItem]:
        """Collect all evidence types for user"""
        since_date = datetime.now() - timedelta(days=days_back)
        
        # Collect merge requests and issues in parallel
        mr_task = self.get_merge_requests(username, since_date)
        issues_task = self.get_issues(username, since_date)
        
        merge_requests, issues = await asyncio.gather(mr_task, issues_task)
        
        return merge_requests + issues
```

**FastAPI Endpoints (Implemented):**
```python
@router.get("/api/evidence/gitlab/health")
async def gitlab_health_check():
    """Check GitLab MCP and API health"""
    client = create_gitlab_client(GITLAB_TOKEN, GITLAB_PROJECT_ID)
    mcp_healthy = await client.check_mcp_health()
    # ... health check implementation

@router.get("/api/evidence/gitlab/collect/{username}")
async def collect_gitlab_evidence(username: str, days_back: int = 7):
    """Collect comprehensive GitLab evidence for user"""
    client = create_gitlab_client(GITLAB_TOKEN, GITLAB_PROJECT_ID)
    evidence_items = await client.get_comprehensive_evidence(username, days_back)
    # ... return formatted response
```

**Data Models (Pydantic):**
```python
@dataclass
class EvidenceItem:
    """Standardized evidence item from any source"""
    id: str
    team_member_id: str
    source: str  # 'gitlab_commit', 'gitlab_mr', 'jira_ticket'
    title: str
    description: str
    source_url: Optional[str]
    category: str  # 'technical', 'collaboration', 'delivery'
    evidence_date: datetime
    created_at: datetime
    metadata: Dict[str, Any]
    data_source: DataSource  # MCP or API
    fallback_used: bool = False
```

**MCP Server Configuration (Confirmed Working):**
```json
{
  "environment": {
    "GITLAB_PERSONAL_ACCESS_TOKEN": "your_gitlab_token",
    "GITLAB_API_URL": "https://gitlab.com/api/v4",
    "GITLAB_READ_ONLY_MODE": "false",
    "USE_GITLAB_WIKI": "true",
    "USE_MILESTONE": "true",
    "USE_PIPELINE": "true"
  },
  "communication": "stdio",
  "tools_available": 65
}
```

**Testing Results (Confirmed Working):**
- ✅ MCP Health: 65 GitLab tools available
- ✅ Data Collection: Merge requests and issues successfully collected
- ✅ API Fallback: Automatic fallback when MCP unavailable
- ✅ Evidence Categorization: Technical, collaboration, delivery categories
- ✅ Production Configuration: Environment variables, no hardcoded secrets

#### 1.2.2: JIRA MCP Integration (Day 5-6) 🚀 **NEXT**
**Tasks:**
- [ ] **JIRA MCP Server**: Set up JIRA MCP server (if available)
- [ ] **Connection Testing**: Test JIRA MCP communication
- [ ] **Hybrid Implementation**: JIRA MCP client with API fallback
- [ ] **Cross-Platform Correlation**: Link GitLab MRs with JIRA tickets
- [ ] **Evidence Transformation**: Convert JIRA data to evidence items

**JIRA Hybrid Client:**
```typescript
export class JIRAHybridClient {
  private mcpClient: JIRAMCPClient | null
  private apiClient: JIRAAPIClient
  
  async getTickets(username: string, fromDate: Date): Promise<JIRATicket[]> {
    // Try MCP first if available
    if (this.mcpClient && await this.checkMCPHealth()) {
      try {
        return await this.mcpClient.searchIssues({
          assignee: username,
          updated: `>=${fromDate.toISOString().split('T')[0]}`,
          maxResults: 100
        })
      } catch (mcpError) {
        console.warn('JIRA MCP failed, falling back to API:', mcpError)
      }
    }
    
    // Fallback to API
    return await this.apiClient.getTickets(username, fromDate)
  }
  
  async correlateWithGitLab(jiraTickets: JIRATicket[], gitlabMRs: EvidenceItem[]): Promise<CorrelationResult[]> {
    // Smart correlation logic using ticket IDs in MR titles/descriptions
    const correlations: CorrelationResult[] = []
    
    for (const ticket of jiraTickets) {
      const relatedMRs = gitlabMRs.filter(mr => 
        mr.title.includes(ticket.key) || 
        mr.description?.includes(ticket.key)
      )
      
      if (relatedMRs.length > 0) {
        correlations.push({
          jiraTicket: ticket,
          gitlabMRs: relatedMRs,
          correlationType: 'ticket_reference'
        })
      }
    }
    
    return correlations
  }
}
```

#### 1.2.3: Evidence Processing Pipeline (Day 6-7)
**Tasks:**
- [ ] **Hybrid Data Integration**: Merge MCP and API data sources
- [ ] **Evidence Categorization**: Smart categorization using combined data
- [ ] **Duplicate Detection**: Cross-platform duplicate detection
- [ ] **Timeline Correlation**: Enhanced correlation with hybrid data
- [ ] **Evidence Browser UI**: Display evidence with source indicators

**Enhanced Evidence Processing:**
```typescript
export class HybridEvidenceProcessor {
  async processHybridData(
    gitlabData: EvidenceItem[], 
    jiraData: JIRATicket[],
    correlations: CorrelationResult[]
  ): Promise<ProcessedEvidence> {
    
    // Categorize evidence using cross-platform context
    const categorized = await this.categorizeWithContext(gitlabData, jiraData, correlations)
    
    // Enhanced duplicate detection across platforms
    const deduplicated = await this.detectCrossPlatformDuplicates(categorized)
    
    // Timeline correlation with JIRA context
    const timeline = await this.buildEnhancedTimeline(deduplicated, correlations)
    
    return {
      evidence: deduplicated,
      timeline: timeline,
      correlations: correlations,
      sources: {
        gitlab: { method: 'MCP', fallback: false },
        jira: { method: 'API', fallback: true }
      }
    }
  }
  
  async detectCrossPlatformDuplicates(items: EvidenceItem[]): Promise<EvidenceItem[]> {
    // Enhanced duplicate detection that considers:
    // 1. GitLab MR linked to JIRA ticket
    // 2. Multiple commits for same JIRA ticket
    // 3. Similar work across different time periods
    
    const groups = new Map<string, EvidenceItem[]>()
    
    for (const item of items) {
      // Group by JIRA ticket reference if present
      const jiraRef = this.extractJIRAReference(item)
      const groupKey = jiraRef || `${item.category}_${item.title.substring(0, 50)}`
      
      if (!groups.has(groupKey)) {
        groups.set(groupKey, [])
      }
      groups.get(groupKey)!.push(item)
    }
    
    // Keep most comprehensive evidence from each group
    return Array.from(groups.values()).map(group => 
      group.reduce((best, current) => 
        current.description.length > best.description.length ? current : best
      )
    )
  }
}
```

**Testing Strategy (Enhanced for Hybrid Approach):**
```typescript
describe('GitLabHybridClient', () => {
  it('should prefer MCP over API when available', async () => {
    const mockMCPResponse = [/* mock MCP data */]
    mockMCPClient.getCommits.mockResolvedValue(mockMCPResponse)
    
    const result = await hybridClient.getCommits('username', new Date())
    
    expect(mockMCPClient.getCommits).toHaveBeenCalled()
    expect(mockAPIClient.getCommits).not.toHaveBeenCalled()
    expect(result).toEqual(expectedEvidenceItems)
  })
  
  it('should fallback to API when MCP fails', async () => {
    const mcpError = new Error('MCP connection failed')
    const mockAPIResponse = [/* mock API data */]
    
    mockMCPClient.getCommits.mockRejectedValue(mcpError)
    mockAPIClient.getCommits.mockResolvedValue(mockAPIResponse)
    
    const result = await hybridClient.getCommits('username', new Date())
    
    expect(mockMCPClient.getCommits).toHaveBeenCalled()
    expect(mockAPIClient.getCommits).toHaveBeenCalled()
    expect(result).toEqual(expectedEvidenceItems)
  })
  
  it('should indicate data source in results', async () => {
    const result = await hybridClient.getCommits('username', new Date())
    
    expect(result.metadata.source).toBe('MCP')
    expect(result.metadata.fallback).toBe(false)
  })
})

describe('Cross-Platform Correlation', () => {
  it('should correlate GitLab MRs with JIRA tickets', async () => {
    const gitlabMRs = [
      { title: 'Fix bug PROJ-123', description: 'Resolves PROJ-123' }
    ]
    const jiraTickets = [
      { key: 'PROJ-123', summary: 'Bug in user login' }
    ]
    
    const correlations = await processor.correlateWithGitLab(jiraTickets, gitlabMRs)
    
    expect(correlations).toHaveLength(1)
    expect(correlations[0].correlationType).toBe('ticket_reference')
  })
})
```

**Acceptance Criteria (Updated for Hybrid Approach):**
- ✅ GitLab MCP integration working (confirmed by testing)
- ✅ GitLab MRs and issues collected via MCP with API fallback
- ✅ Evidence categorized correctly (technical, collaboration, delivery)
- ✅ Data source (MCP vs API) clearly indicated in results
- ✅ System gracefully handles MCP server unavailability
- ✅ FastAPI endpoints for evidence collection implemented
- ✅ Production-ready configuration with environment variables
- ✅ Comprehensive testing and validation completed
- [ ] JIRA tickets and sprint data collected via hybrid approach (Phase 1.2.2)
- [ ] Cross-platform correlation between GitLab and JIRA (Phase 1.2.3)
- [ ] Duplicate evidence detection across platforms (Phase 1.2.3)

---

### Phase 1.3: Basic Document Processing (Days 8-10)
**Goal**: Enable document upload and basic processing for historical context

#### 1.3.1: File Upload System (Day 8)
**Tasks:**
- [ ] Create drag-and-drop file upload interface
- [ ] Implement file validation (type, size limits)
- [ ] Set up Supabase Storage integration
- [ ] Add upload progress tracking
- [ ] Create file management interface

**File Upload Service:**
```typescript
export class FileUploadService {
  async uploadDocument(file: File, teamMemberId: string): Promise<UploadResult>
  async validateFile(file: File): Promise<ValidationResult>
  async getUploadProgress(uploadId: string): Promise<ProgressStatus>
  async deleteDocument(documentId: string): Promise<void>
}
```

**Testing Strategy:**
```typescript
describe('FileUploadService', () => {
  it('should validate file types correctly', async () => {
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const result = await service.validateFile(validFile)
    expect(result.isValid).toBe(true)
  })
  
  it('should reject oversized files', async () => {
    // Test file size limits
  })
  
  it('should upload files to Supabase Storage', async () => {
    // Test successful upload
  })
})
```

#### 1.3.2: Document Processing Pipeline (Day 9-10)
**Tasks:**
- [ ] Implement PDF text extraction
- [ ] Add Word document processing
- [ ] Create JSON parsing for Slack exports
- [ ] Add document type classification
- [ ] Create document viewer interface

**Document Processing:**
```typescript
export class DocumentProcessor {
  async extractText(file: File): Promise<ExtractedText>
  async classifyDocument(content: string): Promise<DocumentType>
  async processSlackExport(jsonData: SlackExport): Promise<ProcessedMessages>
}
```

**Testing Strategy:**
```typescript
describe('DocumentProcessor', () => {
  it('should extract text from PDF files', async () => {
    const pdfBuffer = await readTestPDF('sample.pdf')
    const result = await processor.extractText(pdfBuffer)
    
    expect(result.text).toContain('expected content')
    expect(result.pageCount).toBe(expectedPages)
  })
  
  it('should classify document types accurately', async () => {
    // Test document classification
  })
})
```

**Acceptance Criteria:**
- Managers can upload documents (PDF, Word, JSON) via drag-and-drop
- Text is extracted correctly from uploaded documents
- Document types are classified automatically
- File storage is secure and accessible only to authorized users

---

### Phase 1.4: FastAPI Backend & Integration (Days 11-14) ✅ **PARTIALLY COMPLETE**
**Goal**: Create robust backend for data processing and API endpoints

#### 1.4.1: FastAPI Application Setup (Day 11-12) ✅ **COMPLETE**
**Tasks:**
- [x] Initialize FastAPI project with proper structure
- [x] Set up Pydantic models for data validation
- [x] Implement Supabase integration
- [x] Create API endpoints for evidence management
- [x] Add comprehensive error handling
- [ ] Create API endpoints for team management (frontend handles this)
- [ ] Background job system (future enhancement)

**FastAPI Structure:**
```python
# API Models
class TeamMemberCreate(BaseModel):
    full_name: str
    email: EmailStr
    gitlab_username: Optional[str]
    jira_username: Optional[str]

class EvidenceItem(BaseModel):
    team_member_id: UUID
    source: str
    title: str
    description: str
    category: str
    evidence_date: date

# API Endpoints
@app.get("/api/team-members")
async def get_team_members(current_user: User = Depends(get_current_user)):
    """Get team members for authenticated manager"""
    
@app.post("/api/evidence/collect")
async def collect_evidence(team_member_id: UUID, sources: List[str]):
    """Trigger evidence collection for team member"""
```

**Testing Strategy:**
```python
class TestAPIEndpoints:
    def test_get_team_members_requires_auth(self, client):
        """Should require authentication"""
        response = client.get("/api/team-members")
        assert response.status_code == 401
    
    def test_collect_evidence_respects_consent(self, client, auth_headers):
        """Should only collect data with consent"""
        response = client.post("/api/evidence/collect", 
                             json={"team_member_id": str(uuid4()), "sources": ["gitlab"]},
                             headers=auth_headers)
        # Test consent validation
```

#### 1.4.2: Background Job System (Day 12-13)
**Tasks:**
- [ ] Set up async job queue system
- [ ] Create scheduled sync jobs for GitLab/Jira
- [ ] Implement job status tracking
- [ ] Add retry logic with exponential backoff
- [ ] Create job monitoring interface

**Background Jobs:**
```python
class SyncJobManager:
    async def schedule_evidence_sync(self, team_member_id: UUID, sources: List[str]):
        """Schedule evidence collection job"""
    
    async def process_sync_job(self, job_id: UUID):
        """Process evidence collection job"""
    
    async def get_job_status(self, job_id: UUID) -> JobStatus:
        """Get job processing status"""
```

**Testing Strategy:**
```python
class TestSyncJobs:
    def test_gitlab_sync_job_processes_commits(self, mock_gitlab):
        """Should collect and process GitLab commits"""
        # Mock GitLab API responses
        # Test job execution
    
    def test_job_retry_on_failure(self, mock_failing_api):
        """Should retry failed jobs with backoff"""
        # Test retry logic
```

#### 1.4.3: Basic AI Integration (Day 13-14)
**Tasks:**
- [ ] Set up Claude API integration
- [ ] Implement basic evidence categorization
- [ ] Add simple document theme extraction
- [ ] Create confidence scoring system
- [ ] Add AI processing to evidence pipeline

**AI Integration (MVP):**
```python
class AIService:
    async def categorize_evidence(self, evidence: EvidenceItem) -> CategoryResult:
        """Categorize evidence using Claude API"""
    
    async def extract_document_themes(self, document_text: str) -> List[str]:
        """Extract key themes from uploaded documents"""
    
    async def calculate_confidence_score(self, result: AIResult) -> float:
        """Calculate confidence score for AI results"""
```

**Testing Strategy:**
```python
class TestAIService:
    @patch('anthropic.Anthropic')
    def test_categorize_evidence(self, mock_claude):
        """Should categorize evidence correctly"""
        mock_claude.messages.create.return_value = Mock(
            content=[Mock(text='{"category": "technical", "confidence": 0.95}')]
        )
        
        result = await ai_service.categorize_evidence(sample_evidence)
        assert result.category == "technical"
        assert result.confidence >= 0.9
```

**Acceptance Criteria:**
- FastAPI backend handles all CRUD operations securely
- Background jobs collect evidence data automatically
- AI categorization works with high accuracy (>90%)
- All API endpoints have comprehensive error handling
- Job status can be monitored in real-time

---

## Phase 1 Testing Infrastructure

### Test Configuration & Setup
```typescript
// Frontend Test Setup (jest.config.js)
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  collectCoverageFrom: [
    'app/**/*.{ts,tsx}',
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}
```

```