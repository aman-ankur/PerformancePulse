# PerformancePulse - Simple Component Strategy

## Philosophy: "Use What Exists, Build What's Unique"

Leverage Shadcn/ui for 90% of UI components. Only build custom components for performance management specific features.

---

## Foundation: Shadcn/ui + Tailwind

### Core Setup (Day 1)
```bash
# Initialize Shadcn/ui with sensible defaults
npx shadcn-ui@latest init

# Install essential components in one go
npx shadcn-ui@latest add button input textarea select card
npx shadcn-ui@latest add badge avatar progress skeleton alert 
npx shadcn-ui@latest add dialog sheet popover dropdown-menu
npx shadcn-ui@latest add table tabs command separator
```

### Theme Configuration (Simple)
```typescript
// tailwind.config.ts - Minimal customization
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
          DEFAULT: "hsl(220 70% 50%)", // Nice blue
          foreground: "hsl(0 0% 100%)",
        },
        // Let Shadcn handle the rest
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## Custom Components (Only What's Needed)

### 1. Evidence Components

**EvidenceCard** - Display individual evidence items
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface EvidenceCardProps {
  evidence: {
    id: string
    title: string
    content: string
    source: string
    category?: string
    tags: string[]
    created_at: string
  }
}

export function EvidenceCard({ evidence }: EvidenceCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <Badge variant="secondary">{evidence.source}</Badge>
          <span className="text-xs text-muted-foreground">
            {new Date(evidence.created_at).toLocaleDateString()}
          </span>
        </div>
        <CardTitle className="text-base line-clamp-2">{evidence.title}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
          {evidence.content}
        </p>
        {evidence.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {evidence.tags.map(tag => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

**EvidenceUpload** - File upload with drag & drop
```typescript
import { useState, useCallback } from 'react'
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText, X } from "lucide-react"

export function EvidenceUpload({ onUpload }: { onUpload: (files: File[]) => void }) {
  const [isDragging, setIsDragging] = useState(false)
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    onUpload(files)
  }, [onUpload])

  return (
    <Card 
      className={`border-2 border-dashed p-8 text-center transition-colors ${
        isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
      <h3 className="text-lg font-semibold mb-2">Upload Evidence</h3>
      <p className="text-muted-foreground mb-4">
        Drag and drop files here, or click to select
      </p>
      <Button variant="outline">
        Select Files
      </Button>
    </Card>
  )
}
```

### 2. Insight Components

**InsightCard** - Display AI-generated insights
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Sparkles, ThumbsUp, ThumbsDown } from "lucide-react"

interface InsightCardProps {
  insight: {
    id: string
    type: 'strength' | 'improvement' | 'achievement' | 'trend'
    title: string
    content: string
    confidence: number
    validated: boolean
  }
  onValidate?: (id: string, valid: boolean) => void
}

const insightIcons = {
  strength: "💪",
  improvement: "📈", 
  achievement: "🏆",
  trend: "📊"
}

export function InsightCard({ insight, onValidate }: InsightCardProps) {
  return (
    <Card className="relative">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>{insightIcons[insight.type]}</span>
            <Badge variant="outline" className="capitalize">
              {insight.type}
            </Badge>
          </div>
          <div className="flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-yellow-500" />
            <span className="text-xs text-muted-foreground">
              {Math.round(insight.confidence * 100)}%
            </span>
          </div>
        </div>
        <CardTitle className="text-base">{insight.title}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-sm mb-4">{insight.content}</p>
        {onValidate && !insight.validated && (
          <div className="flex gap-2">
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => onValidate(insight.id, true)}
            >
              <ThumbsUp className="h-3 w-3 mr-1" />
              Helpful
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => onValidate(insight.id, false)}
            >
              <ThumbsDown className="h-3 w-3 mr-1" />
              Not helpful
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

### 3. Dashboard Components

**StatsGrid** - Overview statistics
```typescript
import { Card, CardContent } from "@/components/ui/card"

interface Stat {
  label: string
  value: string | number
  change?: number
  icon?: React.ReactNode
}

export function StatsGrid({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <Card key={index}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </p>
                <p className="text-2xl font-bold">{stat.value}</p>
                {stat.change !== undefined && (
                  <p className={`text-xs ${
                    stat.change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change > 0 ? '+' : ''}{stat.change}% from last period
                  </p>
                )}
              </div>
              {stat.icon && (
                <div className="h-8 w-8 text-muted-foreground">
                  {stat.icon}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

### 4. Layout Components

**AppShell** - Main application layout
```typescript
import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Menu, Home, FileText, Lightbulb, Settings } from "lucide-react"

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Evidence', href: '/evidence', icon: FileText },
  { name: 'Insights', href: '/insights', icon: Lightbulb },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="md:hidden fixed top-4 left-4 z-50">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64">
          <Navigation />
        </SheetContent>
      </Sheet>

      {/* Desktop sidebar */}
      <div className="hidden md:fixed md:inset-y-0 md:flex md:w-64 md:flex-col">
        <div className="flex flex-col flex-grow border-r bg-background px-4 py-6">
          <Navigation />
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-64">
        <main className="px-4 py-6 md:px-8">
          {children}
        </main>
      </div>
    </div>
  )
}

function Navigation() {
  return (
    <nav className="space-y-2">
      {navigation.map(item => (
        <a
          key={item.name}
          href={item.href}
          className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-muted transition-colors"
        >
          <item.icon className="h-4 w-4" />
          {item.name}
        </a>
      ))}
    </nav>
  )
}
```

---

## Utility Components

### Loading States
```typescript
import { Skeleton } from "@/components/ui/skeleton"

export function EvidenceListSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="space-y-3 p-4 border rounded-lg">
          <div className="flex justify-between">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-16 w-full" />
          <div className="flex gap-2">
            <Skeleton className="h-4 w-12" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
      ))}
    </div>
  )
}
```

### Empty States
```typescript
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Plus } from "lucide-react"

export function EmptyState({ 
  icon: Icon = FileText,
  title,
  description,
  action
}: {
  icon?: React.ComponentType<{ className?: string }>
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
}) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-12">
        <Icon className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground text-center mb-6 max-w-sm">
          {description}
        </p>
        {action && (
          <Button onClick={action.onClick}>
            <Plus className="h-4 w-4 mr-2" />
            {action.label}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
```

---

## Form Components (Using React Hook Form)

### Evidence Form
```typescript
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface EvidenceFormData {
  title: string
  content: string
  category: string
  tags: string
}

export function EvidenceForm({ onSubmit }: { onSubmit: (data: EvidenceFormData) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<EvidenceFormData>()

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input
          placeholder="Evidence title"
          {...register("title", { required: "Title is required" })}
        />
        {errors.title && (
          <p className="text-sm text-red-500 mt-1">{errors.title.message}</p>
        )}
      </div>

      <div>
        <Select {...register("category")}>
          <SelectTrigger>
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="technical">Technical</SelectItem>
            <SelectItem value="collaboration">Collaboration</SelectItem>
            <SelectItem value="leadership">Leadership</SelectItem>
            <SelectItem value="delivery">Delivery</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Textarea
          placeholder="Describe your achievement or contribution..."
          rows={4}
          {...register("content", { required: "Content is required" })}
        />
        {errors.content && (
          <p className="text-sm text-red-500 mt-1">{errors.content.message}</p>
        )}
      </div>

      <div>
        <Input
          placeholder="Tags (comma separated)"
          {...register("tags")}
        />
      </div>

      <Button type="submit" className="w-full">
        Save Evidence
      </Button>
    </form>
  )
}
```

---

## Component Organization

### File Structure
```
components/
├── ui/                    # Shadcn components (auto-generated)
├── evidence/
│   ├── evidence-card.tsx
│   ├── evidence-list.tsx
│   ├── evidence-form.tsx
│   └── evidence-upload.tsx
├── insights/
│   ├── insight-card.tsx
│   └── insight-panel.tsx
├── dashboard/
│   ├── stats-grid.tsx
│   └── activity-feed.tsx
├── layout/
│   ├── app-shell.tsx
│   ├── header.tsx
│   └── navigation.tsx
└── common/
    ├── empty-state.tsx
    ├── loading-skeleton.tsx
    └── error-boundary.tsx
```

### Export Pattern
```typescript
// components/evidence/index.ts
export { EvidenceCard } from './evidence-card'
export { EvidenceList } from './evidence-list'
export { EvidenceForm } from './evidence-form'
export { EvidenceUpload } from './evidence-upload'

// Usage in pages
import { EvidenceCard, EvidenceList } from '@/components/evidence'
```

---

## Styling Strategy

### Consistent Patterns
```typescript
// Always use consistent spacing and styling patterns
const cardStyles = "hover:shadow-md transition-shadow cursor-pointer"
const badgeStyles = "text-xs font-medium"
const buttonStyles = "flex items-center gap-2"

// Use Tailwind utilities consistently
const spacing = {
  xs: "p-2",
  sm: "p-4", 
  md: "p-6",
  lg: "p-8"
}
```

### Theme Variables
```css
/* globals.css - Use CSS variables for consistency */
:root {
  --radius: 0.5rem;
  --chart-1: 220 70% 50%;
  --chart-2: 160 60% 45%;
  --chart-3: 30 80% 55%;
}
```

---

## What We're NOT Building

❌ Complex data tables with sorting/filtering
❌ Custom date pickers (use shadcn/ui)
❌ Custom modals/dialogs (use shadcn/ui)
❌ Complex form validation (use react-hook-form)
❌ Custom loading spinners (use shadcn/ui)
❌ Custom tooltips/popovers (use shadcn/ui)

## What We ARE Building

✅ Evidence-specific display components
✅ AI insight presentation components
✅ Simple file upload with drag & drop
✅ Performance dashboard layouts
✅ Empty states for better UX
✅ Loading skeletons for smooth experience

This approach gives us beautiful, accessible components with minimal maintenance overhead while focusing development time on features that differentiate the product.