# Evidence Gathering Improvements

## Current State Analysis
The current evidence gathering system has been implemented with basic fields for storing JIRA and GitLab data. After analyzing the implementation and real data patterns, here are the key improvement points:

### Data Model Improvements

1. **Enhanced Metadata Structure**
   - Current: Generic JSON metadata field
   - Improvement: Add structured fields for common patterns:
     ```sql
     -- For JIRA tickets
     jira_status: text
     jira_priority: text
     jira_epic_link: text
     jira_sprint: text
     jira_components: text[]
     jira_labels: text[]
     
     -- For GitLab
     gitlab_commit_count: integer
     gitlab_lines_added: integer
     gitlab_lines_removed: integer
     gitlab_files_changed: text[]
     gitlab_review_comments: integer
     ```

2. **Evidence Relationships**
   - Add ability to link related evidence items
   - Create a new table for evidence relationships:
     ```sql
     CREATE TABLE evidence_relationships (
       id UUID PRIMARY KEY,
       source_evidence_id UUID REFERENCES evidence_items(id),
       target_evidence_id UUID REFERENCES evidence_items(id),
       relationship_type TEXT,
       strength FLOAT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
     );
     ```

3. **Evidence Context**
   - Add fields for better context tracking:
     ```sql
     project_key: text  -- JIRA project or GitLab project
     team_id: UUID     -- Team context
     sprint_id: text   -- Sprint context
     epic_id: text     -- Epic context
     ```

4. **Evidence Quality Metrics**
   - Add fields to track evidence quality:
     ```sql
     confidence_score: float
     verification_status: text
     last_validated_at: timestamp
     validation_source: text
     ```

### Process Improvements

1. **Real-time Evidence Collection**
   - Implement webhooks for JIRA and GitLab
   - Store evidence as events happen
   - Add timestamp fields for real event times

2. **Evidence Classification**
   - Add ML-based classification for categories
   - Store classification confidence
   - Allow manual override with audit trail

3. **Evidence Deduplication**
   - Add unique constraints for source+platform_id
   - Implement merge strategy for duplicate evidence
   - Track evidence versions

4. **Evidence Enrichment**
   - Add LLM processing results storage
   - Store technology stack mentions
   - Track cross-references between items

### Integration Improvements

1. **JIRA Integration**
   - Store sprint information
   - Track time estimates and actuals
   - Store comment threads
   - Track issue transitions

2. **GitLab Integration**
   - Store code review comments
   - Track CI/CD metrics
   - Store commit message analysis
   - Track branch information

### API Improvements

1. **Evidence Query API**
   - Add filtering by date ranges
   - Add filtering by evidence quality
   - Support relationship queries
   - Enable full-text search

2. **Evidence Analytics API**
   - Add aggregation endpoints
   - Support trend analysis
   - Enable pattern detection
   - Support custom metrics

## Implementation Priority

1. High Priority:
   - Evidence relationships table
   - Enhanced metadata structure
   - Real-time collection via webhooks
   - Deduplication logic

2. Medium Priority:
   - Evidence quality metrics
   - Classification improvements
   - Context tracking fields
   - Analytics API

3. Future Enhancements:
   - ML-based classification
   - Advanced analytics
   - Pattern detection
   - Custom metrics

## Migration Strategy

1. Create new tables without breaking changes
2. Migrate existing data with default values
3. Update APIs to support both old and new fields
4. Gradually transition to new structure

## Impact on Current Features

The proposed improvements will enhance:
- Evidence correlation accuracy
- Data completeness
- Query performance
- Analytics capabilities
- Integration reliability

These improvements should be implemented incrementally to maintain system stability while enhancing functionality. 