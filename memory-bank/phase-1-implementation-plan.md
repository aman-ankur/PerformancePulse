# PerformancePulse - Phase 1 Implementation Plan
## Core Data Pipeline & MVP Foundation

**Philosophy: "Test-First, MVP-Focused, Manager-Centric"**

Build a solid, testable foundation that solves the core problem: collecting and organizing engineering evidence for manager-team member conversations. Focus on essential features that provide immediate value while maintaining high code quality and comprehensive test coverage.

---

## 3-4 Phase Project Overview

### Phase 1 (Weeks 1-2): Core Data Pipeline & MVP Foundation
- **Goal**: Collect and organize evidence from GitLab/Jira with basic processing
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

### Phase 1.2: Data Collection Integration (Days 4-7)
**Goal**: Implement GitLab and Jira data collection with proper consent handling

#### 1.2.1: GitLab MCP Integration (Day 4-5)
**Tasks:**
- [ ] Set up GitLab MCP server connection
- [ ] Implement commit collection with rate limiting
- [ ] Add merge request and code review collection
- [ ] Create data transformation pipeline
- [ ] Add consent-based filtering

**GitLab Data Collection:**
```typescript
export class GitLabMCPClient {
  async getCommits(username: string, fromDate: Date): Promise<GitLabCommit[]>
  async getMergeRequests(username: string, fromDate: Date): Promise<GitLabMR[]>
  async getCodeReviews(username: string, fromDate: Date): Promise<GitLabReview[]>
  
  // Transform to evidence format
  async transformToEvidence(data: GitLabData): Promise<EvidenceItem[]>
}
```

**Testing Strategy:**
```typescript
describe('GitLabMCPClient', () => {
  it('should fetch commits for authorized team members', async () => {
    // Mock GitLab API responses
    const mockCommits = [/* mock data */]
    mockGitLabAPI.getCommits.mockResolvedValue(mockCommits)
    
    const result = await client.getCommits('username', new Date())
    expect(result).toEqual(expectedEvidenceItems)
  })
  
  it('should respect rate limits', async () => {
    // Test rate limiting behavior
  })
  
  it('should handle API failures gracefully', async () => {
    // Test error scenarios
  })
})
```

#### 1.2.2: Jira MCP Integration (Day 5-6)
**Tasks:**
- [ ] Set up Jira MCP server connection
- [ ] Implement ticket collection with filtering
- [ ] Add sprint and project data collection
- [ ] Create cross-platform correlation logic
- [ ] Add consent-based data filtering

**Jira Data Collection:**
```typescript
export class JiraMCPClient {
  async getTickets(username: string, fromDate: Date): Promise<JiraTicket[]>
  async getSprintData(username: string, sprintId: string): Promise<SprintData>
  
  // Correlate with GitLab data
  async correlateWithGitLab(jiraData: JiraTicket[], gitlabData: EvidenceItem[]): Promise<CorrelationResult[]>
}
```

**Testing Strategy:**
```typescript
describe('JiraMCPClient', () => {
  it('should fetch tickets with proper filtering', async () => {
    // Test ticket collection
  })
  
  it('should correlate tickets with GitLab MRs', async () => {
    // Test cross-platform correlation
  })
  
  it('should handle different Jira configurations', async () => {
    // Test various Jira setups
  })
})
```

#### 1.2.3: Evidence Processing Pipeline (Day 6-7)
**Tasks:**
- [ ] Create evidence categorization system
- [ ] Implement duplicate detection
- [ ] Add timeline correlation logic
- [ ] Create evidence browser UI
- [ ] Add filtering and search capabilities

**Evidence Processing:**
```typescript
export class EvidenceProcessor {
  async categorizeEvidence(items: EvidenceItem[]): Promise<CategorizedEvidence[]>
  async detectDuplicates(items: EvidenceItem[]): Promise<DeduplicationResult>
  async correlateByTimeline(items: EvidenceItem[]): Promise<CorrelationGroup[]>
}
```

**Testing Strategy:**
```typescript
describe('EvidenceProcessor', () => {
  it('should categorize evidence correctly', async () => {
    const mockEvidence = [/* test data */]
    const result = await processor.categorizeEvidence(mockEvidence)
    
    expect(result.technical).toHaveLength(expectedTechnicalCount)
    expect(result.collaboration).toHaveLength(expectedCollabCount)
  })
  
  it('should detect duplicate evidence', async () => {
    // Test duplicate detection logic
  })
})
```

**Acceptance Criteria:**
- GitLab commits, MRs, and reviews are collected automatically
- Jira tickets and sprint data are collected with proper filtering
- Evidence is categorized correctly (technical, collaboration, delivery)
- Duplicate evidence is detected and handled
- Only consented data sources are processed

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

### Phase 1.4: FastAPI Backend & Integration (Days 11-14)
**Goal**: Create robust backend for data processing and API endpoints

#### 1.4.1: FastAPI Application Setup (Day 11-12)
**Tasks:**
- [ ] Initialize FastAPI project with proper structure
- [ ] Set up Pydantic models for data validation
- [ ] Implement Supabase integration
- [ ] Create API endpoints for team and evidence management
- [ ] Add comprehensive error handling

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