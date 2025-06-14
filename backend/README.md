# PerformancePulse Backend

FastAPI backend with MCP-first hybrid architecture for evidence collection.

## 🏗️ Architecture

### MCP-First Hybrid Approach

This backend implements a **Model Context Protocol (MCP) first** approach with API fallback:

1. **Primary**: MCP servers for data collection
2. **Fallback**: Direct API calls when MCP fails
3. **Benefits**: Leverage proven MCP ecosystem with reliability guarantee

```
FastAPI Backend
├── GitLab Hybrid Client ✅
│   ├── MCP Client (Primary)
│   └── API Client (Fallback)
└── JIRA Hybrid Client (Future)
    ├── MCP Client (Primary)
    └── API Client (Fallback)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js (for MCP servers)
- GitLab Personal Access Token

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Ensure Node.js and npx are available
npm install -g npx

# Copy configuration template
cp config.example.env .env
# Edit .env with your actual values
```

### Environment Configuration

Create `.env` file with:

```bash
# GitLab Configuration
GITLAB_PERSONAL_ACCESS_TOKEN=your_gitlab_token_here
GITLAB_PROJECT_ID=your_project_id_here
GITLAB_API_URL=https://gitlab.com/api/v4

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# FastAPI Configuration
SECRET_KEY=your_secret_key_here
DEBUG=false
ENVIRONMENT=production
```

### Running the Server

```bash
# Development
uvicorn src.main:app --reload --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🔧 MCP Integration

### GitLab MCP Integration ✅

**Status**: Complete and tested  
**MCP Server**: `@zereight/mcp-gitlab`  
**Tools Available**: 65 GitLab tools

#### Features

- **Merge Requests**: Collect user's merge requests with metadata
- **Issues**: Collect user's issues and assignments
- **Categorization**: Automatic evidence categorization
- **Fallback**: Seamless API fallback on MCP failure
- **Source Tracking**: Track whether data came from MCP or API

#### Usage

```python
from src.services.gitlab_hybrid_client import create_gitlab_client

# Create hybrid client
client = create_gitlab_client(
    gitlab_token="your_token",
    project_id="your_project_id"
)

# Collect evidence (MCP-first with API fallback)
evidence = await client.get_comprehensive_evidence(
    username="gitlab_username",
    days_back=7
)
```

### Testing MCP Integration

```bash
# Set environment variables
export GITLAB_PERSONAL_ACCESS_TOKEN=your_token
export GITLAB_PROJECT_ID=your_project_id
export GITLAB_TEST_USERNAME=test_username

# Run standalone test
python test_gitlab_standalone.py
```

Expected output:
```
🔍 MCP Health: ✅ 65 tools available
📊 Data Collection: ✅ Working
🎯 Overall: ✅ SUCCESS
```

## 📊 API Endpoints

### Evidence Collection

#### Health Check
```
GET /api/evidence/health
GET /api/evidence/gitlab/health
```

#### Evidence Collection
```
GET /api/evidence/gitlab/collect/{username}?days_back=7
```

Response:
```json
{
  "username": "user123",
  "days_back": 7,
  "evidence_count": 15,
  "evidence": [...],
  "collection_summary": {
    "total_items": 15,
    "merge_requests": 8,
    "issues": 7,
    "mcp_items": 12,
    "api_items": 3,
    "fallback_used": true
  }
}
```

#### Specific Data Types
```
GET /api/evidence/gitlab/merge-requests/{username}?days_back=7
GET /api/evidence/gitlab/issues/{username}?days_back=7
```

## 🏗️ Project Structure

```
backend/
├── src/
│   ├── api/
│   │   └── endpoints/
│   │       └── evidence.py          # Evidence collection endpoints
│   ├── services/
│   │   └── gitlab_hybrid_client.py  # MCP-first hybrid client
│   ├── database/
│   │   ├── models.py               # Database models
│   │   └── database.py             # Database connection
│   └── main.py                     # FastAPI application
├── test_gitlab_standalone.py       # MCP integration test
├── config.example.env              # Configuration template
└── requirements.txt                # Python dependencies
```

## 🔒 Security

### Environment Variables

**Never commit sensitive data to git**. All sensitive configuration is handled via environment variables:

- GitLab tokens
- Project IDs
- Database credentials
- API keys

### Configuration Template

Use `config.example.env` as a template and create your own `.env` file with actual values.

## 🧪 Testing

### MCP Integration Test

```bash
# Standalone test (no FastAPI dependencies)
python test_gitlab_standalone.py
```

This test verifies:
- MCP server health (65 tools available)
- GitLab data collection via MCP
- Hybrid fallback mechanism

### API Endpoint Tests

```bash
# Start the server
uvicorn src.main:app --reload

# Test health endpoint
curl http://localhost:8000/api/evidence/health

# Test GitLab health
curl http://localhost:8000/api/evidence/gitlab/health
```

## 🚀 Production Deployment

### Server Requirements

- **Python**: FastAPI application
- **Node.js**: For MCP servers (spawned on-demand)
- **Environment**: All configuration via environment variables

### Deployment Architecture

```
Production Server:
├── FastAPI Application (Python)
│   ├── GitLab Hybrid Client
│   ├── Evidence Collection Endpoints
│   └── Authentication & Database
│
├── Node.js Runtime
│   └── MCP Server (spawned on-demand)
│       └── @zereight/mcp-gitlab
│
└── Environment Configuration
    ├── .env (not in git)
    └── config.example.env (template)
```

**No separate MCP server deployment needed** - MCP servers are spawned as subprocesses when needed.

### Dependencies

```bash
# Python dependencies
pip install fastapi httpx asyncio uvicorn

# Node.js for MCP servers
npm install -g npx
# MCP servers installed automatically via npx
```

## 📈 Performance

### MCP vs API Performance

- **MCP Response Time**: ~2-3 seconds typical
- **API Fallback Time**: ~1-2 seconds typical
- **Hybrid Benefit**: Best of both worlds - MCP ecosystem + API reliability

### Scalability

- **Concurrent Users**: Scalable architecture with async/await
- **Rate Limiting**: Built-in protection in both MCP and API clients
- **Connection Pooling**: Efficient resource usage

## 🔮 Future Enhancements

### Phase 1.2.2: JIRA Integration (Next)

- Research available JIRA MCP servers
- Implement JIRA hybrid client similar to GitLab
- Cross-platform correlation (GitLab MRs ↔ JIRA tickets)

### Phase 1.2.3: Evidence Processing

- Enhanced categorization with AI
- Duplicate detection across platforms
- Timeline correlation and insights

## 📚 Documentation

### Architecture Documentation

- **MCP Architecture**: `../memory-bank/mcp-architecture.md`
- **Implementation Plan**: `../memory-bank/phase-1-implementation-plan.md`
- **System Architecture**: `../memory-bank/system-architecture.md`

### MCP Resources

- **GitLab MCP Server**: https://github.com/zereight/gitlab-mcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Available Tools**: 65 GitLab tools via MCP server

## ✅ Status

### Phase 1.2.1: GitLab MCP Integration - ✅ COMPLETE

- [x] MCP server integration (@zereight/mcp-gitlab)
- [x] Hybrid client implementation
- [x] API fallback mechanism
- [x] Evidence collection endpoints
- [x] Data transformation pipeline
- [x] Testing and verification
- [x] Documentation and security cleanup

**Ready for commit and Phase 1.2.2 (JIRA integration)**

## 🤝 Contributing

1. Follow the MCP-first hybrid approach
2. Add comprehensive tests for new integrations
3. Update documentation for new features
4. Never commit sensitive data - use environment variables

## 📞 Support

For issues with:
- **MCP Integration**: Check MCP server health and Node.js availability
- **API Fallback**: Verify tokens and permissions
- **Configuration**: Use `config.example.env` as reference 