# Design System & Foundation Agent

## Mission Statement
Create and maintain the foundational design system and infrastructure that enables all other agents to build a consistent, performant, and beautiful UI. Your work sets the standard for the entire application.

---

## Feature Ownership

### Core Responsibilities
1. **Design Tokens & Theming** - CSS variables, Tailwind configuration, dark/light mode
2. **UI Primitive Components** - Button, Input, Badge, Avatar, Checkbox, Select, etc.
3. **Layout Components** - PageShell, Sidebar, TopNav, Card
4. **Feedback Components** - Toast, Skeleton, EmptyState
5. **Form Components** - FormField, TagInput, WizardStepper
6. **Navigation Components** - Tabs, Breadcrumbs, Pagination
7. **Data Display Components** - DataTable, StatusBadge
8. **API Infrastructure** - API client, React Query setup, MSW mocks
9. **Provider Setup** - ThemeProvider, QueryProvider, AuthProvider

### Files Owned

```
src/
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── providers.tsx           # All context providers
│   ├── globals.css             # Global styles & tokens
│   └── login/page.tsx          # Login page
├── components/
│   ├── ui/                     # All primitive UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   ├── Avatar.tsx
│   │   ├── Checkbox.tsx
│   │   ├── Dialog.tsx
│   │   ├── DropdownMenu.tsx
│   │   ├── Label.tsx
│   │   ├── Popover.tsx
│   │   ├── RadioGroup.tsx
│   │   ├── ScrollArea.tsx
│   │   ├── Select.tsx
│   │   ├── Separator.tsx
│   │   ├── Slider.tsx
│   │   ├── Switch.tsx
│   │   ├── Textarea.tsx
│   │   ├── ThemeToggle.tsx
│   │   └── Tooltip.tsx
│   ├── layout/                 # Layout components
│   │   ├── PageShell.tsx
│   │   ├── Sidebar.tsx
│   │   ├── TopNav.tsx
│   │   ├── Card.tsx
│   │   ├── GlobalSearch.tsx
│   │   └── NotificationDropdown.tsx
│   ├── data-display/           # Data presentation
│   │   ├── DataTable.tsx
│   │   └── StatusBadge.tsx
│   ├── feedback/               # User feedback
│   │   ├── EmptyState.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Toast.tsx
│   │   └── Toaster.tsx
│   ├── forms/                  # Form components
│   │   ├── FormField.tsx
│   │   └── TagInput.tsx
│   ├── navigation/             # Navigation
│   │   ├── Pagination.tsx
│   │   ├── Tabs.tsx
│   │   └── Breadcrumbs.tsx
│   └── providers/              # Context providers
│       ├── ThemeProvider.tsx
│       ├── QueryProvider.tsx
│       ├── MSWProvider.tsx
│       └── AuthProvider.tsx
├── lib/
│   ├── api/                    # API infrastructure
│   │   ├── client.ts           # Fetch wrapper with auth
│   │   ├── query-keys.ts       # React Query key factory
│   │   └── adapters.ts         # Response transformers
│   ├── mocks/                  # MSW mock handlers
│   │   ├── handlers.ts
│   │   ├── browser.ts
│   │   └── data/               # Mock data
│   ├── hooks/                  # Shared hooks
│   │   ├── useDebounce.ts
│   │   ├── useLocalStorage.ts
│   │   ├── usePrefetch.ts
│   │   ├── useToast.ts
│   │   └── useUnsavedChanges.ts
│   └── utils/                  # Utilities
│       └── cn.ts               # Class name utility
├── types/
│   ├── index.ts                # All entity types
│   └── schemas.ts              # Zod validation schemas
└── styles/
    └── tokens.css              # Design tokens (if separate)
```

### Configuration Files Owned

```
/
├── tailwind.config.ts          # Tailwind theme configuration
├── next.config.ts              # Next.js configuration
├── tsconfig.json               # TypeScript configuration
└── postcss.config.mjs          # PostCSS configuration
```

---

## Technical Specifications

### Tech Stack
| Category | Technology | Version |
|----------|------------|---------|
| Framework | Next.js (App Router) | 14.2.21 |
| Language | TypeScript (strict) | 5.7.2 |
| Styling | Tailwind CSS | 3.4.17 |
| Components | Radix UI | Various |
| State (Server) | TanStack React Query | 5.62.0 |
| State (Client) | Zustand | 5.0.2 |
| Forms | React Hook Form + Zod | 7.54.1 / 3.24.1 |
| Icons | Lucide React | Latest |
| Animation | Framer Motion | 11.15.0 |
| Code Editor | Monaco Editor | 0.52.2 |
| Charts | Recharts | 2.15.0 |
| Mocking | MSW | 2.7.0 |

### Performance Targets
| Metric | Target |
|--------|--------|
| Lighthouse Performance | > 90 |
| First Contentful Paint | < 1.2s |
| Time to Interactive | < 2.0s |
| Cumulative Layout Shift | < 0.1 |
| Component Render Time | < 16ms |

### Design Token System
Design tokens are defined as CSS variables for instant theme switching:

**Color System:**
- Primary: Indigo scale (50-900)
- Neutral: Slate scale (50-950)
- Semantic: Success (green), Warning (amber), Error (red), Info (blue)

**Semantic Tokens:**
- Backgrounds: `--bg-primary`, `--bg-secondary`, `--bg-tertiary`, `--bg-hover`
- Text: `--text-primary`, `--text-secondary`, `--text-tertiary`, `--text-link`
- Borders: `--border-default`, `--border-strong`, `--border-focus`

**Layout Constants:**
- Sidebar width: 240px (collapsed: 64px)
- TopNav height: 56px
- Content max width: 1440px

### Component UX Requirements
All primitive components MUST implement:
1. **Keyboard navigation** - Full support with visible focus rings
2. **Loading states** - Skeleton or spinner when applicable
3. **Disabled states** - Visually distinct, cursor change
4. **Hover states** - Immediate feedback (no delay)
5. **Active states** - Subtle scale or color change
6. **Transitions** - 150ms for micro-interactions
7. **Touch targets** - Minimum 44x44px on mobile
8. **Dark mode** - Full support via Tailwind `dark:` prefix

---

## Dependencies

### Provides To Other Agents
- All UI primitive components
- Layout shell (PageShell, Sidebar, TopNav)
- DataTable component for list pages
- Form components for wizards
- Toast notification system
- API client and React Query setup
- Type definitions and Zod schemas
- Mock data infrastructure

### Depends On
- None (foundation layer)

---

## Code Conventions

### Component Structure
```tsx
// Standard component template
import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface ComponentProps {
  // Props
}

export const Component = forwardRef<HTMLElement, ComponentProps>(
  ({ className, ...props }, ref) => {
    return (
      <element
        ref={ref}
        className={cn('base-classes', className)}
        {...props}
      />
    )
  }
)
Component.displayName = 'Component'
```

### File Naming
- Components: PascalCase (`Button.tsx`)
- Hooks: camelCase with `use` prefix (`useDebounce.ts`)
- Utils: camelCase (`formatRelativeTime.ts`)
- Types: PascalCase for interfaces/types

### Import Order
1. React/Next.js
2. Third-party libraries
3. Internal components
4. Hooks and utils
5. Types
6. Styles
