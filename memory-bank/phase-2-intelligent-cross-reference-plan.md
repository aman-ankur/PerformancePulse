# Phase 2: Intelligent Cross-Reference Detection & Manager Dashboard
## MVP Implementation Plan for Engineering Manager with 3 Team Members

**Status:** Ready to Start  
**Duration:** 2 weeks (Phase 2.1: 1 week, Phase 2.2: 1 week)  
**Build On:** Phase 1.2.3 Unified Evidence Service ✅  
**Goal:** Practical manager tool for 1:1 prep, performance reviews, and team evidence gathering

---

## 🎯 **MVP OVERVIEW**

### **User Context**
- **Role**: Engineering manager with 3 team members
- **Use Cases**: 1:1 meeting prep, performance reviews, evidence gathering for feedback
- **Goal**: Reduce prep time from hours to minutes with accurate correlation
- **Data Sources**: GitLab activity, JIRA tickets, meeting transcripts, documents (RFCs, ADRs)

### **MVP Solution**
Build a practical manager dashboard that:
1. **Correlates GitLab ↔ JIRA** using cost-optimized LLM approach
2. **Collects Evidence** from multiple sources on-demand
3. **Generates Work Stories** with confidence scoring
4. **Provides Meeting Prep** with discussion points and evidence links
5. **Supports Document Upload** for transcripts, RFCs, ADRs

---

## 🧠 **SIMPLIFIED LLM CORRELATION STRATEGY**

### **Problem with Key-Based Approach**
Many teams don't use JIRA keys in Git commits, making traditional correlation ineffective. We need semantic understanding to correlate natural language descriptions.

### **MVP LLM Approach (Good Enough + Cost Manageable)**

#### **Core Principles**
✅ **Smart filtering is essential** - most JIRA-GitLab pairs have zero relationship  
✅ **Embedding similarity is 300x cheaper** than LLM calls and handles obvious correlations well  
✅ **Batch processing reduces token usage** through shared context  
✅ **Context compression preserves semantic meaning** while cutting costs 50-70%  
✅ **LLM for edge cases only** maintains high accuracy without prohibitive costs  

#### **Simple Three-Tier Pipeline**
```
Tier 1: Smart Pre-filtering (Free)
- Author matching (same person = likely related)
- Date proximity (commits >2 weeks after JIRA = unlikely)
- Basic keyword overlap (zero technical terms = unrelated)
→ Eliminates 70-90% of unrelated pairs

Tier 2: Embedding Similarity (~$0.0001/correlation)
- Generate embeddings for JIRA/GitLab content
- Cosine similarity scoring
- High confidence (>0.8) = auto-correlate
- Low confidence (<0.4) = reject
→ Handles 85-90% of remaining correlations

Tier 3: LLM Edge Cases (~$0.01/correlation)
- Only for uncertain cases (0.4-0.8 similarity)
- Batch processing with context compression
- GPT-3.5 Turbo for cost efficiency
→ Resolves final 5-10% with high accuracy
```

#### **Expected Costs for 3 Team Members**
- **Monthly Cost**: $5-15/month total
- **Accuracy**: 90%+ overall correlation accuracy
- **Speed**: <100ms for 95% of correlations
- **Fallback**: Rule-based correlation if LLM budget exceeded

---

## 🏗️ **TECHNICAL ARCHITECTURE**

### **Core Components**

```python
# New correlation engine components:
src/services/correlation_engine.py      # Main correlation orchestration
src/models/correlation_models.py       # Correlation data models
src/algorithms/
├── jira_gitlab_linker.py              # GitLab-JIRA linking logic
├── confidence_scorer.py               # Relationship confidence scoring
├── work_story_grouper.py              # Group related evidence
├── timeline_analyzer.py               # Temporal pattern detection
├── technology_detector.py             # Tech stack identification
├── embedding_correlator.py            # Embedding-based similarity
├── llm_correlator.py                  # LLM-based edge case handling
└── smart_filter.py                    # Pre-filtering logic

# Enhanced existing components:
src/services/unified_evidence_service.py  # Add correlation pipeline
src/models/unified_evidence.py            # Add correlation metadata
```

### **Enhanced Data Flow**

```
Evidence Collection → Smart Pre-Filter → Embedding Similarity → LLM Edge Cases → Work Stories
                                    ↓                      ↓              ↓
                               70-90% filtered      85-90% resolved   95%+ resolved
                               (free)               (~$0.0001/item)   (~$0.01/item)
```

---

## 📋 **PHASE 2.1: LLM CORRELATION (Week 1)**

### **Day 1-2: Simple LLM Service**
```python
# backend/src/services/llm_service.py
class SimpleLLMService:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.embedding_cache = {}
        self.daily_cost = 0.0
        self.daily_limit = 5.0  # $5 daily limit for MVP
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding with basic caching"""
        
    async def correlate_jira_gitlab(self, jira_item: Dict, gitlab_item: Dict) -> Dict:
        """Simple correlation with cost control"""
        
    def smart_prefilter(self, jira_item: Dict, gitlab_item: Dict) -> bool:
        """Basic filtering to eliminate obvious non-matches"""
```

### **Day 3-4: Integration with Existing Engine**
```python
# Enhance existing backend/src/services/correlation_engine.py
class CorrelationEngine:
    def __init__(self):
        # Existing components (already implemented ✅)
        self.jira_gitlab_linker = JiraGitLabLinker()
        self.confidence_scorer = ConfidenceScorer()
        self.work_story_grouper = WorkStoryGrouper()
        
        # NEW: Simple LLM correlator
        self.llm_service = SimpleLLMService()
    
    async def correlate_evidence(self, evidence_items):
        """Enhanced with LLM fallback"""
        # 1. Try rule-based correlation (existing)
        # 2. Use LLM for unmatched items (new)
        # 3. Generate work stories (existing)
```

### **Day 5: Basic API Enhancement**
```python
# backend/src/api/correlation.py
@router.post("/correlate-llm")
async def correlate_with_llm(request: CorrelationRequest):
    """LLM-enhanced correlation endpoint"""
    return {
        "work_stories": result.work_stories,
        "llm_usage": {"cost": cost, "method_breakdown": methods}
    }
```

---

## 📋 **PHASE 2.2: MANAGER DASHBOARD (Week 2)**

### **MVP Dashboard Features**
```
Manager Dashboard for 3 Team Members
├── Team Configuration
│   ├── Hardcode 3 team members initially
│   ├── GitLab/JIRA credentials per member
│   └── Basic profile management
├── Evidence Collection
│   ├── On-demand evidence gathering
│   ├── Work story display with correlation
│   └── Evidence browsing by member/timeframe
├── Meeting Preparation
│   ├── Select team member + timeframe
│   ├── Generated discussion points
│   ├── Evidence links for each point
│   └── Export (PDF/Markdown for 1:1s)
└── Document Upload
    ├── Meeting transcripts
    ├── RFCs, ADRs
    └── Integration with evidence correlation
```

### **Day 1-2: Team Setup & Evidence Collection**
```python
# backend/src/api/manager.py
TEAM_MEMBERS = [
    {"id": "eng1", "name": "Engineer 1", "gitlab_username": "eng1", "jira_username": "eng1@company.com"},
    {"id": "eng2", "name": "Engineer 2", "gitlab_username": "eng2", "jira_username": "eng2@company.com"},
    {"id": "eng3", "name": "Engineer 3", "gitlab_username": "eng3", "jira_username": "eng3@company.com"},
]

@router.get("/team/{member_id}/evidence")
async def get_member_evidence(member_id: str, timeframe: str = "last_month"):
    """Collect evidence using LLM correlation"""
    
@router.post("/evidence/upload")
async def upload_document(file: UploadFile, member_id: str, doc_type: str):
    """Upload meeting transcripts, RFCs, ADRs"""
```

### **Day 3-4: Meeting Prep Interface**
```tsx
// frontend/src/app/dashboard/[memberId]/prep/page.tsx
export default function MeetingPrep({ params }: { params: { memberId: string } }) {
    // Select timeframe, generate discussion points, export functionality
}

// Components:
// - MeetingPrepForm: Select member + timeframe
// - DiscussionPoints: Generated talking points with evidence
// - EvidenceTimeline: Visual timeline of contributions
// - ExportButton: PDF/Markdown export for 1:1s
```

### **Day 5: Document Upload & Integration**

---

## 🎯 **SUCCESS CRITERIA**

### **Phase 2.1 (LLM Correlation)**
- [ ] **Cost Control**: <$15/month for 3 team members
- [ ] **Accuracy**: >85% correlation accuracy (good enough for MVP)
- [ ] **Performance**: <2s response time for correlation requests
- [ ] **Fallback**: Rule-based correlation when LLM budget exceeded

### **Phase 2.2 (Manager Dashboard)**
- [ ] **Time Savings**: Reduce meeting prep from hours to <30 minutes
- [ ] **Evidence Coverage**: Display work stories with confidence scores
- [ ] **Export Quality**: PDF/Markdown suitable for actual 1:1s
- [ ] **Document Integration**: Upload and correlate transcripts, RFCs, ADRs

### **Overall MVP Success**
- [ ] **Real Usage**: Manager uses it for actual team of 3
- [ ] **Value Validation**: Provides actionable insights for performance conversations
- [ ] **Cost Effectiveness**: Total monthly cost <$20 including hosting
- [ ] **Simplicity**: No complex setup - works out of the box

---

## 🔄 **FALLBACK STRATEGY**

### **If LLM Costs Too High**
- **Fallback**: Use existing rule-based correlation from Phase 2.1.1 ✅
- **Reference**: `memory-bank/phase-1-2-3-cross-platform-correlation-plan.md`
- **Capability**: Still provides work stories, just lower accuracy
- **Cost**: $0/month for correlation

### **If LLM Accuracy Insufficient**
- **Enhancement**: Fine-tune prompts based on real team data
- **Hybrid**: Combine rule-based + LLM for better coverage
- **Manual Override**: Allow manager to manually link evidence

---

## 📚 **DOCUMENTATION CLEANUP**

### **Consolidated Files**
1. **This file**: `phase-2-intelligent-cross-reference-plan.md` - Complete Phase 2 plan
2. **Fallback**: `phase-1-2-3-cross-platform-correlation-plan.md` - Rule-based correlation
3. **Progress**: `progress.md` - Updated with current status

### **Removed Redundant Files**
- ❌ `llm-first-implementation.md` - Merged into this file
- ❌ `llm-implementation-roadmap.md` - Merged into this file  
- ❌ `llm-correlation-implementation-plan.md` - Merged into this file
- ❌ `manager-dashboard-implementation.md` - Merged into this file

---

## 🚀 **READY TO START**

**Phase 2.1: LLM Correlation (Week 1)**
- Simple LLM service with cost controls
- Integration with existing correlation engine ✅
- Basic API enhancement

**Phase 2.2: Manager Dashboard (Week 2)**  
- Team configuration for 3 members
- Evidence collection and work story display
- Meeting prep with export functionality
- Document upload integration
