# PerformancePulse - Manager-Focused Component Library

## Philosophy: "Manager-First, Evidence-Driven UI"

Leverage Shadcn/ui for 90% of UI components. Build custom components specifically for manager workflows: team management, evidence organization, historical context integration, and meeting preparation.

---

## Foundation: Shadcn/ui + Tailwind

### Core Setup (Day 1)
```bash
# Initialize Shadcn/ui with professional manager-focused theme
npx shadcn-ui@latest init

# Install essential components for manager dashboard
npx shadcn-ui@latest add button input textarea select card
npx shadcn-ui@latest add badge avatar progress skeleton alert 
npx shadcn-ui@latest add dialog sheet popover dropdown-menu
npx shadcn-ui@latest add table tabs command separator
npx shadcn-ui@latest add calendar date-picker checkbox switch
```

### Manager-Focused Theme Configuration
```typescript
// tailwind.config.ts - Professional manager interface
export default {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(220 70% 50%)", // Professional blue
          foreground: "hsl(0 0% 100%)",
        },
        secondary: {
          DEFAULT: "hsl(210 40% 96%)", // Light gray for cards
          foreground: "hsl(222.2 84% 4.9%)",
        },
        success: "hsl(142 76% 36%)", // Green for positive insights
        warning: "hsl(38 92% 50%)", // Orange for attention items
        destructive: "hsl(0 84% 60%)", // Red for issues
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## Manager Dashboard Components

### 1. Team Management Components

**TeamMemberCard** - Individual team member overview
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Calendar, GitBranch, Ticket, MessageSquare } from "lucide-react"

interface TeamMemberCardProps {
  member: {
    id: string
    name: string
    email: string
    role: string
    level: string
    avatar?: string
    lastOneOnOne?: string
    recentActivity: {
      commits: number
      mergeRequests: number
      tickets: number
      meetings: number
    }
    consentStatus: {
      gitlab: boolean
      jira: boolean
      documents: boolean
    }
  }
  onPrepareOneOnOne: (memberId: string) => void
}

export function TeamMemberCard({ member, onPrepareOneOnOne }: TeamMemberCardProps) {
  const initials = member.name.split(' ').map(n => n[0]).join('')
  
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Avatar>
              <AvatarImage src={member.avatar} />
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-base">{member.name}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {member.role} • Level {member.level}
              </p>
            </div>
          </div>
          <div className="flex gap-1">
            {member.consentStatus.gitlab && (
              <Badge variant="outline" className="text-xs">GitLab</Badge>
            )}
            {member.consentStatus.jira && (
              <Badge variant="outline" className="text-xs">Jira</Badge>
            )}
            {member.consentStatus.documents && (
              <Badge variant="outline" className="text-xs">Docs</Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2 text-sm">
            <GitBranch className="h-4 w-4 text-muted-foreground" />
            <span>{member.recentActivity.commits} commits</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Ticket className="h-4 w-4 text-muted-foreground" />
            <span>{member.recentActivity.tickets} tickets</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>Last 1:1: {member.lastOneOnOne || 'Never'}</span>
          </div>
          <Button 
            size="sm" 
            onClick={() => onPrepareOneOnOne(member.id)}
            className="text-xs"
          >
            Prep 1:1
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

**TeamOverview** - Dashboard summary for managers
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Users, Calendar, GitBranch, AlertTriangle } from "lucide-react"

interface TeamOverviewProps {
  teamStats: {
    totalMembers: number
    activeMembers: number
    upcomingOneOnOnes: number
    overdueOneOnOnes: number
    recentActivity: {
      commits: number
      mergeRequests: number
      tickets: number
    }
  }
}

export function TeamOverview({ teamStats }: TeamOverviewProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Team Size</p>
              <p className="text-2xl font-bold">{teamStats.totalMembers}</p>
              <p className="text-xs text-muted-foreground">
                {teamStats.activeMembers} active this week
              </p>
            </div>
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">1:1s This Week</p>
              <p className="text-2xl font-bold">{teamStats.upcomingOneOnOnes}</p>
              {teamStats.overdueOneOnOnes > 0 && (
                <div className="flex items-center gap-1 text-xs text-orange-600">
                  <AlertTriangle className="h-3 w-3" />
                  <span>{teamStats.overdueOneOnOnes} overdue</span>
                </div>
              )}
            </div>
            <Calendar className="h-8 w-8 text-muted-foreground" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Team Activity</p>
              <p className="text-2xl font-bold">{teamStats.recentActivity.commits}</p>
              <p className="text-xs text-muted-foreground">
                commits this week
              </p>
            </div>
            <GitBranch className="h-8 w-8 text-muted-foreground" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Deliveries</p>
              <p className="text-2xl font-bold">{teamStats.recentActivity.tickets}</p>
              <p className="text-xs text-muted-foreground">
                tickets completed
              </p>
            </div>
            <Badge variant="secondary" className="text-lg">✓</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

### 2. Evidence & Context Components

**EvidenceTimeline** - Chronological view of contributions
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ExternalLink, GitBranch, Ticket, FileText, MessageSquare } from "lucide-react"

interface EvidenceItem {
  id: string
  date: string
  type: 'commit' | 'merge_request' | 'ticket' | 'meeting' | 'document'
  title: string
  description: string
  source: string
  sourceUrl?: string
  category: 'technical' | 'collaboration' | 'leadership' | 'delivery'
}

const typeIcons = {
  commit: GitBranch,
  merge_request: GitBranch,
  ticket: Ticket,
  meeting: MessageSquare,
  document: FileText,
}

const categoryColors = {
  technical: 'bg-blue-100 text-blue-800',
  collaboration: 'bg-green-100 text-green-800',
  leadership: 'bg-purple-100 text-purple-800',
  delivery: 'bg-orange-100 text-orange-800',
}

export function EvidenceTimeline({ evidence }: { evidence: EvidenceItem[] }) {
  return (
    <div className="space-y-4">
      {evidence.map((item, index) => {
        const Icon = typeIcons[item.type]
        return (
          <Card key={item.id} className="relative">
            {index < evidence.length - 1 && (
              <div className="absolute left-6 top-12 bottom-0 w-px bg-border" />
            )}
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-background border rounded-full flex items-center justify-center">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={categoryColors[item.category]} variant="secondary">
                        {item.category}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(item.date).toLocaleDateString()}
                      </span>
                    </div>
                    {item.sourceUrl && (
                      <Button variant="ghost" size="sm" asChild>
                        <a href={item.sourceUrl} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </Button>
                    )}
                  </div>
                  <h4 className="font-medium text-sm mb-1">{item.title}</h4>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {item.description}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Source: {item.source}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
```

**ContextDocumentUpload** - Historical context file upload
```typescript
import { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Upload, FileText, X, Calendar } from "lucide-react"

interface ContextUploadProps {
  teamMemberId: string
  onUpload: (file: File, metadata: ContextMetadata) => void
}

interface ContextMetadata {
  documentType: 'meeting_transcript' | '1_1_notes' | 'slack_thread' | 'performance_summary'
  title: string
  dateRangeStart?: string
  dateRangeEnd?: string
}

export function ContextDocumentUpload({ teamMemberId, onUpload }: ContextUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [metadata, setMetadata] = useState<Partial<ContextMetadata>>({})
  const [isDragging, setIsDragging] = useState(false)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      setSelectedFile(files[0])
    }
  }, [])

  const handleSubmit = () => {
    if (selectedFile && metadata.documentType && metadata.title) {
      onUpload(selectedFile, metadata as ContextMetadata)
      setSelectedFile(null)
      setMetadata({})
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Upload Historical Context</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* File Upload Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
          }`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          {selectedFile ? (
            <div className="flex items-center justify-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              <span className="text-sm font-medium">{selectedFile.name}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedFile(null)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <>
              <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Drop meeting transcripts, 1:1 notes, or Slack exports here
              </p>
              <Button variant="outline" className="mt-2">
                Select File
              </Button>
            </>
          )}
        </div>

        {/* Metadata Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Document Type</label>
            <Select
              value={metadata.documentType}
              onValueChange={(value) => setMetadata(prev => ({ ...prev, documentType: value as any }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="meeting_transcript">Meeting Transcript</SelectItem>
                <SelectItem value="1_1_notes">1:1 Notes</SelectItem>
                <SelectItem value="slack_thread">Slack Thread</SelectItem>
                <SelectItem value="performance_summary">Performance Summary</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Title</label>
            <Input
              placeholder="e.g., Q3 Performance Discussion"
              value={metadata.title || ''}
              onChange={(e) => setMetadata(prev => ({ ...prev, title: e.target.value }))}
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Date Range Start</label>
            <Input
              type="date"
              value={metadata.dateRangeStart || ''}
              onChange={(e) => setMetadata(prev => ({ ...prev, dateRangeStart: e.target.value }))}
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Date Range End</label>
            <Input
              type="date"
              value={metadata.dateRangeEnd || ''}
              onChange={(e) => setMetadata(prev => ({ ...prev, dateRangeEnd: e.target.value }))}
            />
          </div>
        </div>

        <Button
          onClick={handleSubmit}
          disabled={!selectedFile || !metadata.documentType || !metadata.title}
          className="w-full"
        >
          Upload Context Document
        </Button>
      </CardContent>
    </Card>
  )
}
```

---

## Component Organization (Manager-Focused)

### File Structure
```
components/
├── ui/                           # Shadcn components (auto-generated)
├── team/
│   ├── team-member-card.tsx
│   ├── team-overview.tsx
│   ├── consent-management.tsx
│   └── member-profile.tsx
├── evidence/
│   ├── evidence-timeline.tsx
│   ├── evidence-browser.tsx
│   └── evidence-correlation.tsx
├── context/
│   ├── context-document-upload.tsx
│   ├── context-viewer.tsx
│   └── historical-patterns.tsx
├── meetings/
│   ├── meeting-prep-generator.tsx
│   ├── meeting-prep-results.tsx
│   ├── discussion-points.tsx
│   └── meeting-templates.tsx
├── layout/
│   ├── manager-app-shell.tsx
│   ├── dashboard-header.tsx
│   └── navigation.tsx
└── common/
    ├── empty-state.tsx
    ├── loading-skeleton.tsx
    ├── export-dialog.tsx
    └── consent-badge.tsx
```

---

## What We're NOT Building

❌ Employee self-service interfaces
❌ Complex HR workflow components
❌ Performance rating or scoring widgets
❌ Real-time collaboration features
❌ Complex data visualization charts
❌ Goal setting or tracking interfaces

## What We ARE Building

✅ Manager-focused team dashboard components
✅ Historical context upload and processing
✅ Evidence timeline and correlation views
✅ Meeting preparation workflow components
✅ Consent management and privacy controls
✅ Export and sharing capabilities

This component library focuses exclusively on manager workflows for performance conversation preparation, emphasizing evidence organization, historical context integration, and structured meeting preparation. 