# PerformancePulse MCP Architecture
## Model Context Protocol Integration for GitLab Evidence Collection

**Version:** 1.0  
**Status:** Production Ready  
**Phase:** 1.2.1 Complete

---

## 🎯 Overview

PerformancePulse implements a **MCP-first hybrid architecture** for automated evidence collection from GitLab repositories. This approach leverages the proven MCP ecosystem while maintaining reliability through automatic API fallback.

### **Key Benefits**
- **Proven Tools**: Leverage @zereight/mcp-gitlab with 65 available tools
- **Reliability**: Automatic fallback to direct API calls
- **Performance**: Optimized data collection with parallel processing
- **Scalability**: On-demand MCP server spawning
- **Security**: Environment-based configuration, no hardcoded secrets

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
├─────────────────────────────────────────────────────────────┤
│  GitLabHybridClient                                         │
│  ├── GitLabMCPClient (Primary)                             │
│  │   ├── MCP Server: @zereight/mcp-gitlab                  │
│  │   ├── Communication: stdio (JSON-RPC 2.0)              │
│  │   └── Tools: 65 GitLab operations                       │
│  └── GitLabAPIClient (Fallback)                            │
│      ├── Direct HTTP API calls                             │
│      └── Same data format as MCP                           │
├─────────────────────────────────────────────────────────────┤
│  Evidence Processing Pipeline                               │
│  ├── Data Transformation                                   │
│  ├── Categorization (Technical/Collaboration/Delivery)     │
│  └── Standardized EvidenceItem Format                      │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Endpoints                                         │
│  ├── /api/evidence/gitlab/health                           │
│  ├── /api/evidence/gitlab/collect/{username}               │
│  └── /api/evidence/gitlab/merge-requests/{username}        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 MCP Integration Details

### **MCP Server Configuration**
```json
{
  "server": "@zereight/mcp-gitlab",
  "version": "latest",
  "communication": "stdio",
  "protocol": "JSON-RPC 2.0",
  "tools_available": 65,
  "environment": {
    "GITLAB_PERSONAL_ACCESS_TOKEN": "required",
    "GITLAB_API_URL": "https://gitlab.com/api/v4",
    "GITLAB_READ_ONLY_MODE": "false",
    "USE_GITLAB_WIKI": "true",
    "USE_MILESTONE": "true",
    "USE_PIPELINE": "true"
  }
}
```

### **MCP Communication Flow**
1. **Request Formation**: JSON-RPC 2.0 request with method and parameters
2. **Process Spawning**: `npx -y @zereight/mcp-gitlab` with environment
3. **Stdio Communication**: Send request via stdin, receive via stdout
4. **Response Processing**: Parse JSON response and extract data
5. **Error Handling**: Graceful fallback on any MCP failure

### **Available MCP Tools (Key Subset)**
- `list_merge_requests` - Get merge requests with filters
- `get_merge_request` - Get specific MR details
- `list_issues` - Get issues with filters
- `get_issue` - Get specific issue details
- `get_project` - Get project information
- `list_commits` - Get commit history
- And 59+ additional GitLab operations

---

## 🔄 Hybrid Architecture Implementation

### **GitLabHybridClient Class**
```python
class GitLabHybridClient:
    """MCP-first hybrid client with automatic API fallback"""
    
    def __init__(self, gitlab_token: str, project_id: str):
        self.mcp_client = GitLabMCPClient(gitlab_token)
        self.api_client = GitLabAPIClient(gitlab_token)
        self.project_id = project_id
    
    async def get_merge_requests(self, username: str, since_date: datetime) -> List[EvidenceItem]:
        """Get merge requests with MCP-first approach"""
        try:
            # Primary: Try MCP first
            mcp_response = await self.mcp_client.get_merge_requests(
                self.project_id, username, since_date
            )
            if mcp_response.success:
                return self._transform_mcp_data(mcp_response.data, DataSource.MCP)
        except Exception as e:
            logger.warning(f"MCP failed, falling back to API: {e}")
        
        # Fallback: Use direct API
        api_data = await self.api_client.get_merge_requests(
            self.project_id, username, since_date
        )
        return self._transform_api_data(api_data, DataSource.API, fallback_used=True)
```

### **Decision Logic**
1. **Always Try MCP First**: Preferred method for enhanced functionality
2. **Automatic Fallback**: Any MCP failure triggers immediate API fallback
3. **Source Tracking**: Every evidence item tracks which method was used
4. **Performance Monitoring**: Track success rates and response times

---

## 📊 Data Flow & Processing

### **Evidence Collection Pipeline**
```
User Request → GitLabHybridClient → MCP Server (Primary)
                                 ↓ (if fails)
                                 → API Client (Fallback)
                                 ↓
                              Data Transformation
                                 ↓
                              Categorization
                                 ↓
                              EvidenceItem Objects
                                 ↓
                              FastAPI Response
```

### **Data Transformation**
```python
@dataclass
class EvidenceItem:
    """Standardized evidence format from any source"""
    id: str
    team_member_id: str
    source: str  # 'gitlab_mr', 'gitlab_issue'
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

### **Categorization Logic**
- **Technical**: Code changes, bug fixes, feature implementations
- **Collaboration**: Code reviews, discussions, team coordination
- **Delivery**: Project completion, milestone achievements, releases

---

## 🚀 Production Deployment

### **Single Server Architecture**
```
Production Server
├── FastAPI Application (Python)
├── Node.js Runtime (for MCP servers)
├── Environment Configuration
└── On-Demand MCP Server Spawning
```

### **Environment Configuration**
```bash
# Required
GITLAB_PERSONAL_ACCESS_TOKEN=your_gitlab_token
GITLAB_PROJECT_ID=your_project_id

# Optional (with defaults)
GITLAB_API_URL=https://gitlab.com/api/v4
```

### **Deployment Requirements**
- **Python 3.11+**: FastAPI backend
- **Node.js 18+**: MCP server runtime
- **npx**: Package execution for MCP servers
- **Environment Variables**: All configuration externalized

---

## 🛡️ Security & Configuration

### **Security Principles**
- **No Hardcoded Secrets**: All sensitive data via environment variables
- **Minimal Permissions**: Read-only GitLab access tokens
- **Process Isolation**: MCP servers spawned in isolated processes
- **Timeout Protection**: 30-second timeout on all MCP operations

### **Configuration Management**
- **Template**: `config.example.env` (safe for version control)
- **Actual Config**: `.env` files (gitignored)
- **Validation**: Startup checks for required environment variables
- **Fallback Values**: Sensible defaults for optional configuration

---

## 📈 Performance & Monitoring

### **Performance Characteristics**
- **MCP Response Time**: 2-3 seconds typical
- **API Fallback Time**: 1-2 seconds typical
- **Concurrent Requests**: Async/await architecture supports high concurrency
- **Memory Usage**: Minimal (processes spawned on-demand)

### **Monitoring & Observability**
- **Health Checks**: `/api/evidence/gitlab/health` endpoint
- **Success Tracking**: MCP vs API usage statistics
- **Error Logging**: Comprehensive error logging with context
- **Performance Metrics**: Response times and success rates

---

## 🧪 Testing & Validation

### **Test Coverage**
- **MCP Health**: Verify 65 tools available
- **Data Collection**: Successful evidence retrieval
- **Hybrid Fallback**: Automatic API fallback on MCP failure
- **Data Transformation**: Correct EvidenceItem format
- **API Endpoints**: All endpoints functional

### **Test Commands**
```bash
# Health check
curl http://localhost:8000/api/evidence/gitlab/health

# Evidence collection
curl http://localhost:8000/api/evidence/gitlab/collect/username?days_back=7

# Test collection
curl -X POST http://localhost:8000/api/evidence/test-collection?username=testuser
```

---

## 🔮 Future Enhancements

### **Phase 1.2.2: JIRA Integration**
- Similar hybrid architecture for JIRA
- Cross-platform correlation (GitLab ↔ JIRA)
- Enhanced evidence processing

### **Phase 1.2.3: Advanced Processing**
- Duplicate detection across platforms
- Timeline correlation
- AI-powered evidence analysis

### **Scalability Improvements**
- MCP server pooling
- Caching layer
- Background job processing

---

## 📚 References

- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **GitLab MCP Server**: [@zereight/mcp-gitlab](https://www.npmjs.com/package/@zereight/mcp-gitlab)
- **FastAPI Documentation**: [FastAPI](https://fastapi.tiangolo.com/)
- **JSON-RPC 2.0**: [JSON-RPC Specification](https://www.jsonrpc.org/specification)

---

**Status**: ✅ Production Ready  
**Next Phase**: JIRA MCP Integration (Phase 1.2.2) 