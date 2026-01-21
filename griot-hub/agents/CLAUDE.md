# CLAUDE.md - Quick Reference for Claude Code Agents

> **Read this file when starting any session on Griot-Hub.**

---

## Project Overview

**Griot-Hub** is the Next.js frontend for the Enterprise Data Contract Management System. It provides a UI for managing data contracts, assets, quality rules, and compliance reporting.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, Radix UI, TanStack Query, Zustand

---

## Agent Identification

| Working on... | You are | Prompt File | Status File |
|---------------|---------|-------------|-------------|
| UI components, theming, layout, API client, types | **design** | `prompts/design.md` | `status/updates/design.md` |
| Data Assets, Database Connections, Schema viewer | **schema** | `prompts/schema.md` | `status/updates/schema.md` |
| Data Contracts, Quality Rules, Wizards, YAML editor | **contracts** | `prompts/contracts.md` | `status/updates/contracts.md` |
| Dashboard, Reports, Marketplace, Timeline | **dashboards** | `prompts/dashboards-reports.md` | `status/updates/dashboards.md` |
| Tasks, Issues, Admin, Settings, Global Search | **platform** | `prompts/platform.md` | `status/updates/platform.md` |
| Testing, Visual regression, Accessibility, Polish | **qa** | `prompts/qa.md` | `status/updates/qa.md` |
| Coordination, task assignment, integration | **orchestrator** | — | `status/board.md` |

---

## Core Rules

### Rule 1: Stay in Your Lane
Only modify files in your owned feature area. Check your prompt file for what you own.

### Rule 2: Request When Blocked
Need something from another agent? Create `agents/status/requests/REQ-<3-digit-number>.md`

### Rule 3: Always Read (in order)
1. `agents/status/board.md` - Current tasks and priorities
2. `agents/status/updates/*.md` - Exit notes from other agents
3. `agents/status/requests/*.md` - Requests from other agents
4. `agents/status/responses/*` - Responses to your requests
5. `agents/prompts/<your-agent>.md` - Your feature responsibilities

### Rule 4: Always Write (in order)
1. Your code changes in `src/`
2. Exit notes in `agents/status/updates/<your-agent>.md`
3. Requests in `agents/status/requests/REQ-<3-digit-number>.md` (if blocked)
4. Responses in `agents/status/responses/RES-<3-digit-number>.md` (to requests for you)
5. Test docs in `agents/status/tests/<your-agent>-tests.md`

---

## Directory Structure

```
griot-hub/
├── src/
│   ├── app/                    # Next.js pages (App Router)
│   ├── components/             # React components
│   │   ├── ui/                 # Primitive UI components
│   │   ├── layout/             # Layout components
│   │   ├── dashboard/          # Dashboard-specific
│   │   ├── contracts/          # Contract-specific
│   │   ├── assets/             # Asset-specific
│   │   └── ...
│   ├── lib/
│   │   ├── api/                # API client, query keys
│   │   ├── mocks/              # MSW handlers and mock data
│   │   └── hooks/              # Custom hooks
│   └── types/                  # TypeScript types
├── tests/                      # Playwright tests
├── agents/
│   ├── prompts/                # Agent responsibility specs
│   └── status/                 # Status tracking
│       ├── board.md            # Task board (orchestrator only)
│       ├── updates/            # Agent exit notes
│       ├── requests/           # Cross-agent requests
│       ├── responses/          # Request responses
│       └── tests/              # Test documentation
└── public/                     # Static assets
```

---

## Common Workflows

### Starting a Session
```bash
# 1. Read the board for your tasks
cat agents/status/board.md

# 2. Check for updates from other agents
ls agents/status/updates/

# 3. Check for requests directed at you
ls agents/status/requests/

# 4. Read your prompt file for context
cat agents/prompts/<your-agent>.md
```

### Ending a Session
```bash
# 1. Update your status file
# Write what you did, what's pending, any blockers

# 2. Commit your changes
git add src/ agents/status/updates/<your-agent>.md
git commit -m "feat(<component>): <description>"
```

### Creating a Request
```markdown
# agents/status/requests/REQ-001.md

## Request: [Short Title]
**From:** schema
**To:** design
**Priority:** High | Medium | Low
**Blocking:** Yes | No

### Description
What you need from the other agent.

### Context
Why you need it.

### Deadline (if any)
When you need it by.
```

### Responding to a Request
```markdown
# agents/status/responses/RES-001.md

## Response to REQ-001
**From:** design
**Status:** Completed | In Progress | Cannot Do

### Resolution
What was done or why it can't be done.

### Files Changed
- path/to/file.tsx
```

---

## Status Board Rules

| Action | Who Can Do It |
|--------|---------------|
| Edit `board.md` | **orchestrator ONLY** |
| Edit `status/updates/<agent>.md` | That specific agent |
| Create `status/requests/REQ-NNN.md` | Any agent |
| Create `status/responses/RES-NNN.md` | Agent responding |

**Why?** Multiple agents editing board.md causes merge conflicts.

---

## Code Conventions

### Component Files
```tsx
// src/components/ui/Button.tsx
import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps { /* ... */ }

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, ...props }, ref) => (
    <button ref={ref} className={cn('...', className)} {...props} />
  )
)
Button.displayName = 'Button'
```

### Page Files
```tsx
// src/app/studio/contracts/page.tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { PageShell } from '@/components/layout/PageShell'

export default function ContractsPage() {
  const { data, isLoading } = useQuery({ /* ... */ })

  return (
    <PageShell>
      {/* Page content */}
    </PageShell>
  )
}
```

### Mock Handlers
```typescript
// src/lib/mocks/handlers/contracts.ts
import { http, HttpResponse } from 'msw'

export const contractHandlers = [
  http.get('/api/contracts', () => {
    return HttpResponse.json({ data: mockContracts })
  }),
]
```

---

## Quick Commands

```bash
# Development
npm run dev           # Start dev server
npm run build         # Production build
npm run lint          # Run ESLint

# Testing
npm run test:e2e      # Run Playwright tests
npm run test:e2e:ui   # Playwright UI mode

# Storybook
npm run storybook     # Component documentation
```

---

## Key Files Reference

| Purpose | Path |
|---------|------|
| Root layout | `src/app/layout.tsx` |
| Global styles | `src/app/globals.css` |
| Tailwind config | `tailwind.config.ts` |
| Type definitions | `src/types/index.ts` |
| API client | `src/lib/api/client.ts` |
| Query keys | `src/lib/api/query-keys.ts` |
| MSW setup | `src/lib/mocks/browser.ts` |
| Playwright config | `playwright.config.ts` |
