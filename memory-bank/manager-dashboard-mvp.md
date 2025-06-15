# Manager Dashboard MVP Implementation
## Practical Tool for Engineering Managers with Multi-Source Evidence Correlation

**Status:** Ready for Implementation (Phase 2.2)  
**Timeline:** 1 week  
**Dependencies:** Phase 2.1 LLM Correlation ✅  
**Goal:** Reduce meeting prep from hours to <30 minutes with rich, multi-source evidence

---

## 🎯 **MVP VISION**

### **Multi-Source Evidence Platform**
Build a comprehensive manager dashboard that correlates evidence from multiple sources to provide rich, actionable insights for performance management.

### **Data Source Ecosystem**
```
Evidence Sources
├── Development Platforms
│   ├── GitLab (commits, MRs, issues) ✅
│   ├── JIRA (tickets, comments, workflows) ✅
│   ├── GitHub (future)
│   └── Bitbucket (future)
├── Communication Platforms
│   ├── Slack (messages, threads, reactions)
│   ├── Microsoft Teams (future)
│   └── Discord (future)
├── Documentation Sources
│   ├── Meeting Transcripts (upload/integration)
│   ├── RFCs & ADRs (authored documents)
│   ├── Confluence (future)
│   └── Notion (future)
├── Performance Data
│   ├── Code Review Comments
│   ├── Deployment Metrics
│   ├── Incident Response
│   └── Knowledge Sharing
└── Custom Sources
    ├── Survey Responses
    ├── Peer Feedback
    └── Goal Tracking
```

### **Core Value Proposition**
- **Unified Evidence**: Correlate activities across all platforms
- **Rich Context**: Understand not just what was done, but how and why
- **Actionable Insights**: Generate discussion points with supporting evidence
- **Extensible Platform**: Easy to add new data sources and connectors

---

## 🏗️ **ARCHITECTURE DESIGN**

### **Connector-Based Architecture**
```
Manager Dashboard
├── Data Connectors
│   ├── GitLab Connector ✅
│   ├── JIRA Connector ✅
│   ├── Slack Connector (new)
│   ├── Document Connector (new)
│   └── Custom Connector Framework
├── Correlation Engine
│   ├── LLM-Enhanced Correlation ✅
│   ├── Cross-Platform Linking
│   ├── Temporal Analysis
│   └── Context Enrichment
├── Evidence Processing
│   ├── Multi-Source Aggregation
│   ├── Duplicate Detection
│   ├── Confidence Scoring
│   └── Work Story Generation
└── Manager Interface
    ├── Team Overview Dashboard
    ├── Member Deep Dive
    ├── Meeting Preparation
    └── Evidence Export
```

### **Extensible Connector Framework**
```python
# backend/src/connectors/base_connector.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models.unified_evidence import UnifiedEvidenceItem

class BaseConnector(ABC):
    """Base class for all evidence connectors"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    async def collect_evidence(self, user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect evidence for a user within timeframe"""
        pass
    
    @abstractmethod
    def get_connector_info(self) -> Dict[str, Any]:
        """Return connector metadata and capabilities"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection and return status"""
        pass
```

---

## 📋 **IMPLEMENTATION PLAN**

### **Day 1: Connector Framework & Team Management**

#### **Connector Registry**
```python
# backend/src/services/connector_registry.py
from typing import Dict, Type, List
from src.connectors.base_connector import BaseConnector
from src.connectors.gitlab_connector import GitLabConnector
from src.connectors.jira_connector import JiraConnector
from src.connectors.slack_connector import SlackConnector
from src.connectors.document_connector import DocumentConnector

class ConnectorRegistry:
    """Registry for all available connectors"""
    
    def __init__(self):
        self.connectors: Dict[str, Type[BaseConnector]] = {
            'gitlab': GitLabConnector,
            'jira': JiraConnector,
            'slack': SlackConnector,
            'documents': DocumentConnector,
        }
        self.active_connectors: Dict[str, BaseConnector] = {}
    
    async def initialize_connector(self, connector_type: str, credentials: Dict[str, str]) -> bool:
        """Initialize and authenticate a connector"""
        if connector_type not in self.connectors:
            raise ValueError(f"Unknown connector type: {connector_type}")
        
        connector_class = self.connectors[connector_type]
        connector = connector_class()
        
        if await connector.authenticate(credentials):
            self.active_connectors[connector_type] = connector
            return True
        return False
    
    async def collect_all_evidence(self, user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect evidence from all active connectors"""
        all_evidence = []
        
        for connector_type, connector in self.active_connectors.items():
            try:
                evidence = await connector.collect_evidence(user_id, timeframe)
                all_evidence.extend(evidence)
            except Exception as e:
                print(f"Error collecting from {connector_type}: {e}")
        
        return all_evidence
    
    def get_available_connectors(self) -> List[Dict[str, Any]]:
        """Get list of all available connectors"""
        return [
            {
                "type": connector_type,
                "name": connector_class().get_connector_info()["name"],
                "description": connector_class().get_connector_info()["description"],
                "active": connector_type in self.active_connectors
            }
            for connector_type, connector_class in self.connectors.items()
        ]
```

#### **Team Management API**
```python
# backend/src/api/manager.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from src.services.connector_registry import ConnectorRegistry
from src.services.correlation_engine import CorrelationEngine

router = APIRouter(prefix="/api/manager")

# Dynamic team management (no hardcoding)
@router.get("/team")
async def get_team():
    """Get all team members from database/config"""
    # TODO: Implement dynamic team loading
    return {"team_members": []}

@router.post("/team/member")
async def add_team_member(member_data: TeamMemberRequest):
    """Add a new team member"""
    # TODO: Implement team member creation
    pass

@router.get("/connectors")
async def get_available_connectors():
    """Get all available data connectors"""
    registry = ConnectorRegistry()
    return {"connectors": registry.get_available_connectors()}

@router.post("/connectors/{connector_type}/configure")
async def configure_connector(connector_type: str, credentials: ConnectorCredentials):
    """Configure and activate a data connector"""
    registry = ConnectorRegistry()
    
    success = await registry.initialize_connector(
        connector_type, 
        credentials.dict()
    )
    
    if success:
        return {"success": True, "message": f"{connector_type} connector activated"}
    else:
        raise HTTPException(status_code=400, detail="Failed to authenticate connector")

@router.get("/connectors/{connector_type}/test")
async def test_connector(connector_type: str):
    """Test connector connection"""
    registry = ConnectorRegistry()
    
    if connector_type not in registry.active_connectors:
        raise HTTPException(status_code=404, detail="Connector not configured")
    
    connector = registry.active_connectors[connector_type]
    result = await connector.test_connection()
    
    return result
```

### **Day 2: Slack Connector Implementation**

#### **Slack Evidence Connector**
```python
# backend/src/connectors/slack_connector.py
import asyncio
from typing import List, Dict, Any
from slack_sdk.web.async_client import AsyncWebClient
from src.connectors.base_connector import BaseConnector
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, EvidenceType

class SlackConnector(BaseConnector):
    """Slack evidence collector"""
    
    def __init__(self):
        self.client = None
        self.bot_token = None
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Slack using bot token"""
        try:
            self.bot_token = credentials.get('bot_token')
            self.client = AsyncWebClient(token=self.bot_token)
            
            # Test authentication
            response = await self.client.auth_test()
            return response["ok"]
        except Exception as e:
            print(f"Slack authentication failed: {e}")
            return False
    
    async def collect_evidence(self, user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect Slack evidence for user"""
        if not self.client:
            return []
        
        evidence_items = []
        
        try:
            # Get user's Slack ID
            slack_user_id = await self._get_slack_user_id(user_id)
            if not slack_user_id:
                return []
            
            # Collect different types of Slack evidence
            evidence_items.extend(await self._collect_messages(slack_user_id, timeframe))
            evidence_items.extend(await self._collect_thread_participation(slack_user_id, timeframe))
            evidence_items.extend(await self._collect_reactions_given(slack_user_id, timeframe))
            evidence_items.extend(await self._collect_channel_activity(slack_user_id, timeframe))
            
        except Exception as e:
            print(f"Error collecting Slack evidence: {e}")
        
        return evidence_items
    
    async def _collect_messages(self, slack_user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect user's messages and their context"""
        messages = []
        
        # Get conversations user is part of
        conversations = await self.client.conversations_list(
            types="public_channel,private_channel,mpim,im"
        )
        
        for channel in conversations["channels"]:
            try:
                # Get messages from user in this channel
                history = await self.client.conversations_history(
                    channel=channel["id"],
                    oldest=self._timeframe_to_timestamp(timeframe)
                )
                
                user_messages = [
                    msg for msg in history["messages"] 
                    if msg.get("user") == slack_user_id and msg.get("text")
                ]
                
                for msg in user_messages:
                    evidence_item = UnifiedEvidenceItem(
                        id=f"slack_msg_{msg['ts']}",
                        platform_type=PlatformType.SLACK,
                        evidence_type=EvidenceType.COMMUNICATION,
                        title=f"Message in #{channel['name']}",
                        description=msg["text"][:500],
                        author=slack_user_id,
                        created_at=self._timestamp_to_datetime(msg["ts"]),
                        url=f"https://slack.com/app_redirect?channel={channel['id']}&message_ts={msg['ts']}",
                        metadata={
                            "channel_name": channel["name"],
                            "channel_id": channel["id"],
                            "message_type": "channel_message",
                            "thread_ts": msg.get("thread_ts"),
                            "reaction_count": len(msg.get("reactions", []))
                        }
                    )
                    messages.append(evidence_item)
                    
            except Exception as e:
                print(f"Error collecting from channel {channel['name']}: {e}")
        
        return messages
    
    async def _collect_thread_participation(self, slack_user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect user's participation in threads"""
        # Implementation for thread participation analysis
        return []
    
    async def _collect_reactions_given(self, slack_user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect reactions given by user (engagement indicator)"""
        # Implementation for reaction analysis
        return []
    
    async def _collect_channel_activity(self, slack_user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect user's channel joining/leaving activity"""
        # Implementation for channel activity
        return []
    
    def get_connector_info(self) -> Dict[str, Any]:
        """Return Slack connector information"""
        return {
            "name": "Slack",
            "description": "Collect communication evidence from Slack workspace",
            "evidence_types": [
                "Channel messages",
                "Thread participation", 
                "Reactions and engagement",
                "Channel activity"
            ],
            "required_credentials": ["bot_token"],
            "setup_instructions": "Create a Slack app with bot token and required scopes"
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Slack connection"""
        if not self.client:
            return {"status": "error", "message": "Not authenticated"}
        
        try:
            response = await self.client.auth_test()
            return {
                "status": "success",
                "message": "Connected to Slack",
                "workspace": response.get("team"),
                "bot_user": response.get("user")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

### **Day 3: Document Connector & Upload System**

#### **Document Evidence Connector**
```python
# backend/src/connectors/document_connector.py
from typing import List, Dict, Any
import re
from datetime import datetime
from src.connectors.base_connector import BaseConnector
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, EvidenceType

class DocumentConnector(BaseConnector):
    """Document evidence collector for uploaded files"""
    
    def __init__(self):
        self.document_store = {}  # In-memory for MVP, use database in production
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """No authentication needed for document uploads"""
        return True
    
    async def collect_evidence(self, user_id: str, timeframe: str) -> List[UnifiedEvidenceItem]:
        """Collect document evidence for user"""
        user_docs = self.document_store.get(user_id, [])
        
        # Filter by timeframe
        filtered_docs = [
            doc for doc in user_docs 
            if self._is_within_timeframe(doc.created_at, timeframe)
        ]
        
        return filtered_docs
    
    async def process_meeting_transcript(
        self, 
        content: str, 
        user_id: str, 
        meeting_date: str,
        attendees: List[str] = None
    ) -> UnifiedEvidenceItem:
        """Process uploaded meeting transcript"""
        
        # Extract insights from transcript
        insights = self._analyze_transcript(content)
        
        evidence_item = UnifiedEvidenceItem(
            id=f"transcript_{user_id}_{meeting_date}_{datetime.now().timestamp()}",
            platform_type=PlatformType.DOCUMENT,
            evidence_type=EvidenceType.MEETING_TRANSCRIPT,
            title=f"Meeting Transcript - {meeting_date}",
            description=self._extract_summary(content),
            author=user_id,
            created_at=datetime.fromisoformat(meeting_date),
            metadata={
                "document_type": "meeting_transcript",
                "attendees": attendees or [],
                "topics_discussed": insights["topics"],
                "action_items": insights["action_items"],
                "decisions_made": insights["decisions"],
                "technical_discussions": insights["technical_content"],
                "collaboration_indicators": insights["collaboration"]
            }
        )
        
        # Store document
        if user_id not in self.document_store:
            self.document_store[user_id] = []
        self.document_store[user_id].append(evidence_item)
        
        return evidence_item
    
    async def process_technical_document(
        self,
        content: str,
        user_id: str,
        doc_type: str,  # "rfc", "adr", "design_doc", "postmortem"
        title: str,
        created_date: str = None
    ) -> UnifiedEvidenceItem:
        """Process technical documents (RFCs, ADRs, etc.)"""
        
        # Analyze technical content
        analysis = self._analyze_technical_document(content, doc_type)
        
        evidence_item = UnifiedEvidenceItem(
            id=f"{doc_type}_{user_id}_{datetime.now().timestamp()}",
            platform_type=PlatformType.DOCUMENT,
            evidence_type=EvidenceType.TECHNICAL_DOCUMENT,
            title=title,
            description=analysis["summary"],
            author=user_id,
            created_at=datetime.fromisoformat(created_date) if created_date else datetime.now(),
            metadata={
                "document_type": doc_type,
                "technical_decisions": analysis["decisions"],
                "technologies_mentioned": analysis["technologies"],
                "complexity_indicators": analysis["complexity"],
                "stakeholders_mentioned": analysis["stakeholders"],
                "impact_scope": analysis["impact"],
                "quality_indicators": analysis["quality"]
            }
        )
        
        # Store document
        if user_id not in self.document_store:
            self.document_store[user_id] = []
        self.document_store[user_id].append(evidence_item)
        
        return evidence_item
    
    def _analyze_transcript(self, content: str) -> Dict[str, List[str]]:
        """Analyze meeting transcript for insights"""
        lines = content.split('\n')
        
        insights = {
            "topics": [],
            "action_items": [],
            "decisions": [],
            "technical_content": [],
            "collaboration": []
        }
        
        for line in lines:
            line_lower = line.lower()
            
            # Extract action items
            if any(keyword in line_lower for keyword in ['action:', 'todo:', 'follow up', 'will do', 'assigned to']):
                insights["action_items"].append(line.strip())
            
            # Extract decisions
            if any(keyword in line_lower for keyword in ['decided', 'decision:', 'agreed', 'conclusion']):
                insights["decisions"].append(line.strip())
            
            # Extract technical content
            if any(keyword in line_lower for keyword in ['api', 'database', 'architecture', 'implementation', 'code', 'system']):
                insights["technical_content"].append(line.strip())
            
            # Extract collaboration indicators
            if any(keyword in line_lower for keyword in ['team', 'collaborate', 'help', 'support', 'mentor', 'review']):
                insights["collaboration"].append(line.strip())
        
        # Extract topics (simplified - can be enhanced with NLP)
        insights["topics"] = self._extract_topics_simple(content)
        
        return insights
    
    def _analyze_technical_document(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Analyze technical documents for insights"""
        analysis = {
            "summary": content[:300] + "..." if len(content) > 300 else content,
            "decisions": [],
            "technologies": [],
            "complexity": "medium",
            "stakeholders": [],
            "impact": "team",
            "quality": {}
        }
        
        content_lower = content.lower()
        
        # Extract technologies
        tech_keywords = [
            'python', 'javascript', 'react', 'fastapi', 'postgresql', 'redis', 
            'docker', 'kubernetes', 'aws', 'microservice', 'api', 'database'
        ]
        analysis["technologies"] = [
            tech for tech in tech_keywords 
            if tech in content_lower
        ]
        
        # Assess complexity
        complexity_indicators = len(re.findall(r'\b(complex|difficult|challenging|intricate)\b', content_lower))
        if complexity_indicators > 3:
            analysis["complexity"] = "high"
        elif complexity_indicators > 1:
            analysis["complexity"] = "medium"
        else:
            analysis["complexity"] = "low"
        
        # Extract decisions (for ADRs)
        if doc_type == "adr":
            decision_patterns = [
                r'we will (.+?)(?:\.|$)',
                r'decision: (.+?)(?:\.|$)',
                r'chosen (.+?)(?:\.|$)'
            ]
            for pattern in decision_patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                analysis["decisions"].extend(matches)
        
        return analysis
    
    def get_connector_info(self) -> Dict[str, Any]:
        """Return document connector information"""
        return {
            "name": "Documents",
            "description": "Process uploaded documents for evidence extraction",
            "evidence_types": [
                "Meeting transcripts",
                "RFCs (Request for Comments)",
                "ADRs (Architecture Decision Records)",
                "Design documents",
                "Postmortem reports"
            ],
            "required_credentials": [],
            "setup_instructions": "No setup required - upload documents directly"
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test document connector"""
        return {
            "status": "success",
            "message": "Document connector ready",
            "stored_documents": sum(len(docs) for docs in self.document_store.values())
        }
```

### **Day 4: Enhanced Evidence Collection & Correlation**

#### **Multi-Source Evidence Service**
```python
# backend/src/services/multi_source_evidence_service.py
from typing import List, Dict, Any
from src.services.connector_registry import ConnectorRegistry
from src.services.correlation_engine import CorrelationEngine
from src.models.unified_evidence import UnifiedEvidenceItem

class MultiSourceEvidenceService:
    """Enhanced evidence service with multi-source correlation"""
    
    def __init__(self):
        self.connector_registry = ConnectorRegistry()
        self.correlation_engine = CorrelationEngine()
    
    async def collect_comprehensive_evidence(
        self, 
        user_id: str, 
        timeframe: str,
        source_filters: List[str] = None
    ) -> Dict[str, Any]:
        """Collect evidence from all configured sources"""
        
        # Collect from all active connectors
        all_evidence = await self.connector_registry.collect_all_evidence(user_id, timeframe)
        
        # Filter by source if specified
        if source_filters:
            all_evidence = [
                item for item in all_evidence 
                if item.platform_type.value in source_filters
            ]
        
        # Group evidence by source
        evidence_by_source = {}
        for item in all_evidence:
            source = item.platform_type.value
            if source not in evidence_by_source:
                evidence_by_source[source] = []
            evidence_by_source[source].append(item)
        
        # Apply LLM-enhanced correlation
        correlation_result = await self.correlation_engine.correlate_evidence(
            CorrelationRequest(
                evidence_items=all_evidence,
                use_llm_correlation=True
            )
        )
        
        # Generate enriched insights
        enriched_insights = self._generate_enriched_insights(
            correlation_result.correlated_collection,
            evidence_by_source
        )
        
        return {
            "total_evidence_items": len(all_evidence),
            "evidence_by_source": {
                source: len(items) for source, items in evidence_by_source.items()
            },
            "work_stories": correlation_result.correlated_collection.work_stories,
            "cross_platform_relationships": correlation_result.relationships_detected,
            "enriched_insights": enriched_insights,
            "correlation_metadata": {
                "processing_time_ms": correlation_result.processing_time_ms,
                "llm_cost": correlation_result.metadata.get("llm_cost", 0.0),
                "confidence_distribution": self._analyze_confidence_distribution(correlation_result)
            }
        }
    
    def _generate_enriched_insights(
        self, 
        correlated_collection: Any, 
        evidence_by_source: Dict[str, List[UnifiedEvidenceItem]]
    ) -> Dict[str, Any]:
        """Generate insights enriched by multi-source data"""
        
        insights = {
            "communication_patterns": self._analyze_communication_patterns(evidence_by_source),
            "technical_contributions": self._analyze_technical_contributions(evidence_by_source),
            "collaboration_indicators": self._analyze_collaboration_indicators(evidence_by_source),
            "knowledge_sharing": self._analyze_knowledge_sharing(evidence_by_source),
            "cross_platform_activity": self._analyze_cross_platform_activity(evidence_by_source)
        }
        
        return insights
    
    def _analyze_communication_patterns(self, evidence_by_source: Dict) -> Dict[str, Any]:
        """Analyze communication patterns across platforms"""
        slack_messages = evidence_by_source.get('slack', [])
        meeting_transcripts = evidence_by_source.get('document', [])
        
        return {
            "slack_activity": len(slack_messages),
            "meeting_participation": len([
                doc for doc in meeting_transcripts 
                if doc.evidence_type.value == 'meeting_transcript'
            ]),
            "communication_frequency": "high" if len(slack_messages) > 50 else "medium" if len(slack_messages) > 20 else "low"
        }
    
    def _analyze_technical_contributions(self, evidence_by_source: Dict) -> Dict[str, Any]:
        """Analyze technical contributions across platforms"""
        gitlab_items = evidence_by_source.get('gitlab', [])
        technical_docs = [
            doc for doc in evidence_by_source.get('document', [])
            if doc.evidence_type.value == 'technical_document'
        ]
        
        return {
            "code_contributions": len(gitlab_items),
            "technical_documentation": len(technical_docs),
            "technologies_used": list(set([
                tech for item in gitlab_items + technical_docs
                for tech in item.metadata.get('technologies', [])
            ]))
        }
```

### **Day 5: Frontend Dashboard with Connector Management**

#### **Connector Configuration Interface**
```tsx
// frontend/src/app/dashboard/connectors/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { CheckCircle, XCircle, Settings, Plus } from 'lucide-react'

interface Connector {
  type: string
  name: string
  description: string
  active: boolean
  evidence_types: string[]
  required_credentials: string[]
}

export default function ConnectorManagement() {
  const [connectors, setConnectors] = useState<Connector[]>([])
  const [loading, setLoading] = useState(true)
  const [configuring, setConfiguring] = useState<string | null>(null)

  useEffect(() => {
    loadConnectors()
  }, [])

  const loadConnectors = async () => {
    try {
      const response = await fetch('/api/manager/connectors')
      const data = await response.json()
      setConnectors(data.connectors)
    } catch (error) {
      console.error('Failed to load connectors:', error)
    } finally {
      setLoading(false)
    }
  }

  const configureConnector = async (connectorType: string, credentials: any) => {
    try {
      const response = await fetch(`/api/manager/connectors/${connectorType}/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      
      if (response.ok) {
        await loadConnectors() // Refresh connector status
        setConfiguring(null)
      }
    } catch (error) {
      console.error('Failed to configure connector:', error)
    }
  }

  const testConnector = async (connectorType: string) => {
    try {
      const response = await fetch(`/api/manager/connectors/${connectorType}/test`)
      const result = await response.json()
      alert(`Test result: ${result.message}`)
    } catch (error) {
      console.error('Failed to test connector:', error)
    }
  }

  if (loading) return <div className="p-6">Loading connectors...</div>

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Data Source Connectors</h1>
        <p className="text-gray-600 mt-2">
          Configure data sources to enrich evidence collection
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {connectors.map(connector => (
          <Card key={connector.type} className="relative">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{connector.name}</span>
                <div className="flex items-center space-x-2">
                  {connector.active ? (
                    <Badge variant="default" className="bg-green-500">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="secondary">
                      <XCircle className="w-3 h-3 mr-1" />
                      Inactive
                    </Badge>
                  )}
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-600">{connector.description}</p>
                
                <div>
                  <h4 className="font-medium mb-2">Evidence Types:</h4>
                  <div className="flex flex-wrap gap-1">
                    {connector.evidence_types.map(type => (
                      <Badge key={type} variant="outline" className="text-xs">
                        {type}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex space-x-2">
                  {!connector.active ? (
                    <Button 
                      size="sm"
                      onClick={() => setConfiguring(connector.type)}
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Configure
                    </Button>
                  ) : (
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => testConnector(connector.type)}
                    >
                      Test Connection
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Configuration Modal */}
      {configuring && (
        <ConnectorConfigModal
          connector={connectors.find(c => c.type === configuring)!}
          onSave={(credentials) => configureConnector(configuring, credentials)}
          onCancel={() => setConfiguring(null)}
        />
      )}
    </div>
  )
}

// Connector configuration modal component
function ConnectorConfigModal({ connector, onSave, onCancel }: any) {
  const [credentials, setCredentials] = useState<any>({})

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Configure {connector.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {connector.required_credentials.map((field: string) => (
              <div key={field}>
                <label className="block text-sm font-medium mb-2">
                  {field.replace('_', ' ').toUpperCase()}
                </label>
                <Input
                  type={field.includes('token') || field.includes('key') ? 'password' : 'text'}
                  value={credentials[field] || ''}
                  onChange={(e) => setCredentials({
                    ...credentials,
                    [field]: e.target.value
                  })}
                  placeholder={`Enter ${field}`}
                />
              </div>
            ))}
            
            <div className="flex space-x-2 pt-4">
              <Button onClick={() => onSave(credentials)} className="flex-1">
                Save Configuration
              </Button>
              <Button variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

#### **Enhanced Evidence Dashboard**
```tsx
// frontend/src/app/dashboard/[memberId]/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { GitBranch, MessageSquare, FileText, Users, Code, Clock } from 'lucide-react'

interface EvidenceData {
  total_evidence_items: number
  evidence_by_source: Record<string, number>
  work_stories: any[]
  enriched_insights: any
  correlation_metadata: any
}

export default function MemberEvidence({ params }: { params: { memberId: string } }) {
  const [evidenceData, setEvidenceData] = useState<EvidenceData | null>(null)
  const [loading, setLoading] = useState(false)
  const [timeframe, setTimeframe] = useState('last_month')
  const [sourceFilters, setSourceFilters] = useState<string[]>([])

  const loadEvidence = async () => {
    setLoading(true)
    try {
      const queryParams = new URLSearchParams({
        timeframe,
        ...(sourceFilters.length > 0 && { sources: sourceFilters.join(',') })
      })
      
      const response = await fetch(
        `/api/manager/team/${params.memberId}/evidence?${queryParams}`
      )
      const data = await response.json()
      setEvidenceData(data)
    } catch (error) {
      console.error('Failed to load evidence:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadEvidence()
  }, [params.memberId, timeframe, sourceFilters])

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'gitlab': return <GitBranch className="w-4 h-4" />
      case 'jira': return <FileText className="w-4 h-4" />
      case 'slack': return <MessageSquare className="w-4 h-4" />
      case 'document': return <FileText className="w-4 h-4" />
      default: return <Code className="w-4 h-4" />
    }
  }

  if (loading) return <div className="p-6">Loading evidence...</div>

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Team Member Evidence</h1>
        <div className="flex items-center space-x-4 mt-4">
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="last_week">Last Week</SelectItem>
              <SelectItem value="last_month">Last Month</SelectItem>
              <SelectItem value="last_quarter">Last Quarter</SelectItem>
            </SelectContent>
          </Select>
          
          <Button onClick={loadEvidence} disabled={loading}>
            Refresh Evidence
          </Button>
        </div>
      </div>

      {evidenceData && (
        <>
          {/* Evidence Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-gray-600">Total Evidence</p>
                    <p className="text-2xl font-bold">{evidenceData.total_evidence_items}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {Object.entries(evidenceData.evidence_by_source).map(([source, count]) => (
              <Card key={source}>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    {getSourceIcon(source)}
                    <div>
                      <p className="text-sm text-gray-600 capitalize">{source}</p>
                      <p className="text-2xl font-bold">{count}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Enriched Insights */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Multi-Source Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Communication</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Slack Activity</span>
                      <Badge variant="outline">
                        {evidenceData.enriched_insights.communication_patterns?.slack_activity || 0}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Meeting Participation</span>
                      <Badge variant="outline">
                        {evidenceData.enriched_insights.communication_patterns?.meeting_participation || 0}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Technical</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Code Contributions</span>
                      <Badge variant="outline">
                        {evidenceData.enriched_insights.technical_contributions?.code_contributions || 0}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Documentation</span>
                      <Badge variant="outline">
                        {evidenceData.enriched_insights.technical_contributions?.technical_documentation || 0}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Collaboration</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Cross-Platform Activity</span>
                      <Badge variant="outline">High</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Knowledge Sharing</span>
                      <Badge variant="outline">Medium</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Work Stories */}
          <Card>
            <CardHeader>
              <CardTitle>Work Stories ({evidenceData.work_stories.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {evidenceData.work_stories.map((story, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-semibold">{story.title}</h4>
                    <p className="text-gray-600 text-sm mb-2">{story.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {story.timeline?.duration || 'N/A'}
                      </span>
                      <span className="flex items-center">
                        <Users className="w-3 h-3 mr-1" />
                        {story.evidence_items?.length || 0} items
                      </span>
                      <Badge variant="outline">
                        {(story.confidence_score * 100).toFixed(0)}% confidence
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
```

---

## 🎯 **SUCCESS CRITERIA**

### **Multi-Source Integration**
- [ ] **Connector Framework**: Extensible system for adding new data sources
- [ ] **Active Connectors**: GitLab ✅, JIRA ✅, Slack, Documents
- [ ] **Evidence Correlation**: Cross-platform relationship detection
- [ ] **Rich Context**: Enhanced insights from multiple sources

### **Manager Experience**
- [ ] **Unified Dashboard**: Single view of all team member activities
- [ ] **Connector Management**: Easy setup and configuration of data sources
- [ ] **Evidence Quality**: Actionable insights with confidence scores
- [ ] **Export Capability**: Meeting prep materials suitable for 1:1s

### **Technical Excellence**
- [ ] **Performance**: <5s for multi-source evidence collection
- [ ] **Cost Control**: <$20/month including LLM and hosting
- [ ] **Extensibility**: Easy to add new connectors and evidence types
- [ ] **Reliability**: Graceful handling of connector failures

---

## 🚀 **FUTURE CONNECTOR ROADMAP**

### **Phase 3: Additional Connectors**
- **GitHub**: Code contributions and collaboration
- **Microsoft Teams**: Communication and meeting data
- **Confluence**: Documentation and knowledge sharing
- **Linear**: Issue tracking and project management
- **Figma**: Design collaboration and feedback

### **Phase 4: Advanced Features**
- **Real-time Sync**: Live updates from connected platforms
- **Custom Connectors**: User-defined data source integrations
- **AI Insights**: Advanced pattern recognition across sources
- **Team Analytics**: Comparative analysis and benchmarking

**Ready for Implementation**: Comprehensive manager dashboard with extensible multi-source evidence correlation 