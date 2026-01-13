# Agent 0: Design System & Foundation

## Mission Statement
Create the foundational design system and infrastructure that enables all other agents to build a consistent, performant, and beautiful UI. Your work sets the standard for the entire application.

---

## Critical Success Metrics

| Metric | Target |
|--------|--------|
| Lighthouse Performance | > 90 |
| First Contentful Paint | < 1.2s |
| Time to Interactive | < 2.0s |
| Cumulative Layout Shift | < 0.1 |
| Component Render Time | < 16ms |

---

## Tech Stack

```
Framework:        Next.js 14+ (App Router)
Language:         TypeScript (strict mode)
Styling:          Tailwind CSS + CSS Variables
Components:       Radix UI primitives (headless)
State:            Zustand (global) + React Query (server)
Forms:            React Hook Form + Zod
Icons:            Lucide React
Animation:        Framer Motion
Code Editor:      Monaco Editor
Charts:           Recharts
Mocking:          MSW (Mock Service Worker)
Testing:          Playwright + Vitest
```

---

## Project Structure

```
griot/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout
│   │   ├── providers.tsx         # All providers
│   │   ├── loading.tsx           # Global loading
│   │   └── error.tsx             # Global error
│   │
│   ├── components/
│   │   ├── ui/                   # Primitive components
│   │   ├── layout/               # Layout components
│   │   ├── data-display/         # Data presentation
│   │   ├── feedback/             # User feedback
│   │   ├── forms/                # Form components
│   │   └── navigation/           # Navigation
│   │
│   ├── lib/
│   │   ├── api/                  # API client
│   │   ├── mocks/                # MSW mocks
│   │   ├── hooks/                # Shared hooks
│   │   ├── utils/                # Utilities
│   │   └── stores/               # Zustand stores
│   │
│   ├── types/                    # TypeScript types
│   └── styles/                   # Global styles
│
├── public/                       # Static assets
├── tests/                        # Test files
└── .storybook/                   # Storybook config
```

---

## Task Specifications

### A0-01: Project Setup

**Objective**: Initialize Next.js project with optimal configuration for performance.

**Requirements**:
```bash
# Create Next.js app
npx create-next-app@latest griot --typescript --tailwind --app --src-dir

# Install core dependencies
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu \
  @radix-ui/react-tabs @radix-ui/react-tooltip @radix-ui/react-select \
  @radix-ui/react-checkbox @radix-ui/react-radio-group \
  @radix-ui/react-switch @radix-ui/react-popover \
  zustand @tanstack/react-query \
  react-hook-form @hookform/resolvers zod \
  lucide-react framer-motion \
  recharts @monaco-editor/react \
  msw clsx tailwind-merge \
  date-fns
```

**next.config.js optimizations**:
```javascript
const nextConfig = {
  // Enable React strict mode
  reactStrictMode: true,
  
  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
  },
  
  // Enable experimental features for performance
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
}
```

**TypeScript strict configuration** (tsconfig.json):
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

---

### A0-02: Design Tokens

**Objective**: Create comprehensive design tokens using CSS variables for instant theme switching.

**File**: `src/styles/tokens.css`

```css
:root {
  /* ============================================
     COLOR SYSTEM
     ============================================ */
  
  /* Primary - Indigo */
  --color-primary-50: 238 242 255;
  --color-primary-100: 224 231 255;
  --color-primary-200: 199 210 254;
  --color-primary-300: 165 180 252;
  --color-primary-400: 129 140 248;
  --color-primary-500: 99 102 241;
  --color-primary-600: 79 70 229;
  --color-primary-700: 67 56 202;
  --color-primary-800: 55 48 163;
  --color-primary-900: 49 46 129;
  
  /* Neutral - Slate */
  --color-neutral-50: 248 250 252;
  --color-neutral-100: 241 245 249;
  --color-neutral-200: 226 232 240;
  --color-neutral-300: 203 213 225;
  --color-neutral-400: 148 163 184;
  --color-neutral-500: 100 116 139;
  --color-neutral-600: 71 85 105;
  --color-neutral-700: 51 65 85;
  --color-neutral-800: 30 41 59;
  --color-neutral-900: 15 23 42;
  --color-neutral-950: 2 6 23;
  
  /* Semantic Colors */
  --color-success: 34 197 94;
  --color-success-light: 220 252 231;
  --color-warning: 245 158 11;
  --color-warning-light: 254 243 199;
  --color-error: 239 68 68;
  --color-error-light: 254 226 226;
  --color-info: 59 130 246;
  --color-info-light: 219 234 254;
  
  /* ============================================
     SEMANTIC TOKENS (Light Theme)
     ============================================ */
  
  /* Backgrounds */
  --bg-primary: var(--color-neutral-50);
  --bg-secondary: 255 255 255;
  --bg-tertiary: var(--color-neutral-100);
  --bg-inverse: var(--color-neutral-900);
  --bg-brand: var(--color-primary-500);
  --bg-hover: var(--color-neutral-100);
  --bg-active: var(--color-neutral-200);
  
  /* Text */
  --text-primary: var(--color-neutral-900);
  --text-secondary: var(--color-neutral-600);
  --text-tertiary: var(--color-neutral-400);
  --text-inverse: 255 255 255;
  --text-brand: var(--color-primary-600);
  --text-link: var(--color-primary-600);
  --text-link-hover: var(--color-primary-700);
  
  /* Borders */
  --border-default: var(--color-neutral-200);
  --border-strong: var(--color-neutral-300);
  --border-focus: var(--color-primary-500);
  
  /* ============================================
     TYPOGRAPHY
     ============================================ */
  
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Font Sizes */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* ============================================
     SPACING
     ============================================ */
  
  --space-0: 0;
  --space-1: 0.25rem;    /* 4px */
  --space-2: 0.5rem;     /* 8px */
  --space-3: 0.75rem;    /* 12px */
  --space-4: 1rem;       /* 16px */
  --space-5: 1.25rem;    /* 20px */
  --space-6: 1.5rem;     /* 24px */
  --space-8: 2rem;       /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */
  
  /* ============================================
     LAYOUT
     ============================================ */
  
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 64px;
  --topnav-height: 56px;
  --content-max-width: 1440px;
  
  /* ============================================
     EFFECTS
     ============================================ */
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
  --transition-slow: 300ms ease;
  
  /* Z-Index Scale */
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal-backdrop: 300;
  --z-modal: 400;
  --z-popover: 500;
  --z-tooltip: 600;
  --z-toast: 700;
}

/* ============================================
   DARK THEME
   ============================================ */

[data-theme="dark"] {
  --bg-primary: var(--color-neutral-950);
  --bg-secondary: var(--color-neutral-900);
  --bg-tertiary: var(--color-neutral-800);
  --bg-inverse: var(--color-neutral-50);
  --bg-hover: var(--color-neutral-800);
  --bg-active: var(--color-neutral-700);
  
  --text-primary: var(--color-neutral-50);
  --text-secondary: var(--color-neutral-400);
  --text-tertiary: var(--color-neutral-500);
  --text-inverse: var(--color-neutral-900);
  --text-brand: var(--color-primary-400);
  --text-link: var(--color-primary-400);
  --text-link-hover: var(--color-primary-300);
  
  --border-default: var(--color-neutral-800);
  --border-strong: var(--color-neutral-700);
}
```

**Tailwind integration** (`tailwind.config.ts`):
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'rgb(var(--color-primary-50) / <alpha-value>)',
          // ... all shades
        },
        bg: {
          primary: 'rgb(var(--bg-primary) / <alpha-value>)',
          secondary: 'rgb(var(--bg-secondary) / <alpha-value>)',
          // ...
        },
        text: {
          primary: 'rgb(var(--text-primary) / <alpha-value>)',
          // ...
        }
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)'],
      },
      spacing: {
        'sidebar': 'var(--sidebar-width)',
        'sidebar-collapsed': 'var(--sidebar-collapsed-width)',
        'topnav': 'var(--topnav-height)',
      },
      transitionDuration: {
        'fast': '150ms',
        'normal': '200ms',
        'slow': '300ms',
      }
    }
  }
}
```

---

### A0-03: Theme System

**Objective**: Implement instant theme switching with no flash.

**File**: `src/lib/hooks/useTheme.ts`

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'system'

interface ThemeStore {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
}

export const useTheme = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: 'system',
      resolvedTheme: 'light',
      setTheme: (theme) => {
        const resolved = theme === 'system' 
          ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
          : theme
        
        document.documentElement.setAttribute('data-theme', resolved)
        set({ theme, resolvedTheme: resolved })
      }
    }),
    { name: 'griot-theme' }
  )
)
```

**Theme script for preventing flash** (`src/app/theme-script.tsx`):
```tsx
export function ThemeScript() {
  const script = `
    (function() {
      const stored = localStorage.getItem('griot-theme');
      const theme = stored ? JSON.parse(stored).state.theme : 'system';
      const resolved = theme === 'system'
        ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
        : theme;
      document.documentElement.setAttribute('data-theme', resolved);
    })();
  `;
  
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
```

---

### A0-04: Primitive UI Components

**Objective**: Build foundational UI components with Radix UI for accessibility.

#### Button Component

**File**: `src/components/ui/Button.tsx`

```tsx
import { forwardRef } from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  // Base styles - MUST include focus-visible for keyboard nav
  `inline-flex items-center justify-center whitespace-nowrap rounded-md
   text-sm font-medium transition-colors duration-fast
   focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500
   focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
   active:scale-[0.98]`, // Subtle press feedback
  {
    variants: {
      variant: {
        primary: `bg-primary-600 text-white hover:bg-primary-700 
                  shadow-sm hover:shadow-md`,
        secondary: `bg-bg-secondary text-text-primary border border-border-default
                    hover:bg-bg-hover hover:border-border-strong`,
        ghost: `hover:bg-bg-hover text-text-secondary hover:text-text-primary`,
        danger: `bg-error text-white hover:bg-red-600`,
        link: `text-text-link underline-offset-4 hover:underline`,
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-9 px-4',
        lg: 'h-10 px-6',
        icon: 'h-9 w-9',
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    }
  }
)

export interface ButtonProps 
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild, loading, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    
    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {children}
      </Comp>
    )
  }
)
Button.displayName = 'Button'
```

#### Input Component

**File**: `src/components/ui/Input.tsx`

```tsx
import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, leftIcon, rightIcon, ...props }, ref) => {
    return (
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary">
            {leftIcon}
          </div>
        )}
        <input
          ref={ref}
          className={cn(
            `flex h-9 w-full rounded-md border bg-bg-secondary px-3 py-2
             text-sm text-text-primary placeholder:text-text-tertiary
             transition-colors duration-fast
             focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
             disabled:cursor-not-allowed disabled:opacity-50`,
            error 
              ? 'border-error focus:ring-error' 
              : 'border-border-default hover:border-border-strong',
            leftIcon && 'pl-10',
            rightIcon && 'pr-10',
            className
          )}
          {...props}
        />
        {rightIcon && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary">
            {rightIcon}
          </div>
        )}
      </div>
    )
  }
)
Input.displayName = 'Input'
```

#### Additional Primitives Required:
- `Select` - Using Radix Select
- `Checkbox` - Using Radix Checkbox
- `RadioGroup` - Using Radix RadioGroup
- `Switch` - Using Radix Switch (for dark mode)
- `Tooltip` - Using Radix Tooltip
- `Badge` - Status indicators
- `Avatar` - User avatars
- `Dropdown` - Using Radix DropdownMenu

**UX REQUIREMENTS FOR ALL PRIMITIVES**:
1. **Keyboard navigation** - Full support, visible focus rings
2. **Loading states** - Skeleton or spinner when loading
3. **Disabled states** - Visually distinct, cursor change
4. **Hover states** - Immediate feedback (no delay)
5. **Active states** - Subtle scale or color change
6. **Transitions** - 150ms for micro-interactions
7. **Touch targets** - Minimum 44x44px on mobile

---

### A0-05: Layout Components

**Objective**: Build the app shell and layout primitives.

#### PageShell Component

**File**: `src/components/layout/PageShell.tsx`

```tsx
'use client'

import { useState } from 'react'
import { Sidebar } from './Sidebar'
import { TopNav } from './TopNav'
import { cn } from '@/lib/utils'

interface PageShellProps {
  children: React.ReactNode
}

export function PageShell({ children }: PageShellProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  
  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Sidebar */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      
      {/* Main content area */}
      <div 
        className={cn(
          "transition-[margin] duration-normal",
          sidebarCollapsed ? "ml-sidebar-collapsed" : "ml-sidebar"
        )}
      >
        {/* Top navigation */}
        <TopNav />
        
        {/* Page content */}
        <main className="min-h-[calc(100vh-var(--topnav-height))] p-6">
          <div className="mx-auto max-w-[var(--content-max-width)]">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
```

#### Sidebar Component (with instant interactions)

**File**: `src/components/layout/Sidebar.tsx`

```tsx
'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Home, Palette, Store, Settings, Moon, Sun, 
  ChevronLeft, Database, FileText, CheckSquare, AlertCircle
} from 'lucide-react'
import { useTheme } from '@/lib/hooks/useTheme'
import { cn } from '@/lib/utils'
import { Tooltip } from '@/components/ui/Tooltip'

const mainNavItems = [
  { 
    label: 'Home', 
    href: '/', 
    icon: Home,
    description: 'Dashboard & Overview'
  },
  { 
    label: 'Studio', 
    href: '/studio', 
    icon: Palette,
    description: 'Manage contracts & assets',
    children: [
      { label: 'Data Assets', href: '/studio/assets', icon: Database },
      { label: 'Data Contracts', href: '/studio/contracts', icon: FileText },
      { label: 'My Tasks', href: '/studio/tasks', icon: CheckSquare },
      { label: 'Issues', href: '/studio/issues', icon: AlertCircle },
    ]
  },
  { 
    label: 'Marketplace', 
    href: '/marketplace', 
    icon: Store,
    description: 'Discover data assets'
  },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname()
  const { theme, resolvedTheme, setTheme } = useTheme()
  
  // Determine active section for highlighting
  const activeSection = mainNavItems.find(item => 
    pathname === item.href || pathname.startsWith(item.href + '/')
  )
  
  return (
    <aside 
      className={cn(
        "fixed left-0 top-0 h-screen bg-bg-secondary border-r border-border-default",
        "flex flex-col transition-[width] duration-normal z-sticky",
        collapsed ? "w-sidebar-collapsed" : "w-sidebar"
      )}
    >
      {/* Logo */}
      <div className="h-topnav flex items-center px-4 border-b border-border-default">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">G</span>
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="font-semibold text-text-primary overflow-hidden"
              >
                Griot
              </motion.span>
            )}
          </AnimatePresence>
        </Link>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-y-auto">
        <div className="px-3 space-y-1">
          {/* Section label */}
          {!collapsed && (
            <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider px-3 mb-2 block">
              Focused
            </span>
          )}
          
          {mainNavItems.map((item) => (
            <NavItem 
              key={item.href}
              item={item}
              collapsed={collapsed}
              isActive={pathname === item.href || pathname.startsWith(item.href + '/')}
              pathname={pathname}
            />
          ))}
        </div>
      </nav>
      
      {/* Bottom section */}
      <div className="border-t border-border-default p-3 space-y-1">
        {!collapsed && (
          <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider px-3 mb-2 block">
            System
          </span>
        )}
        
        {/* Settings */}
        <NavLink 
          href="/settings" 
          icon={Settings} 
          label="Settings"
          collapsed={collapsed}
          isActive={pathname.startsWith('/settings')}
        />
        
        {/* Theme toggle */}
        <button
          onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
          className={cn(
            "w-full flex items-center gap-3 px-3 py-2 rounded-md",
            "text-text-secondary hover:text-text-primary hover:bg-bg-hover",
            "transition-colors duration-fast"
          )}
        >
          {resolvedTheme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          {!collapsed && <span>{resolvedTheme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>}
        </button>
      </div>
      
      {/* Collapse toggle */}
      <button
        onClick={onToggle}
        className={cn(
          "absolute -right-3 top-20 w-6 h-6 rounded-full",
          "bg-bg-secondary border border-border-default",
          "flex items-center justify-center",
          "hover:bg-bg-hover transition-colors duration-fast",
          "shadow-sm"
        )}
      >
        <ChevronLeft 
          size={14} 
          className={cn(
            "transition-transform duration-normal",
            collapsed && "rotate-180"
          )} 
        />
      </button>
    </aside>
  )
}

// NavItem with children support
function NavItem({ item, collapsed, isActive, pathname }) {
  const [expanded, setExpanded] = useState(isActive)
  const hasChildren = item.children && item.children.length > 0
  
  // Auto-expand if child is active
  useEffect(() => {
    if (hasChildren && item.children.some(c => pathname.startsWith(c.href))) {
      setExpanded(true)
    }
  }, [pathname])
  
  if (hasChildren && !collapsed) {
    return (
      <div>
        <button
          onClick={() => setExpanded(!expanded)}
          className={cn(
            "w-full flex items-center justify-between px-3 py-2 rounded-md",
            "transition-colors duration-fast",
            isActive 
              ? "bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400"
              : "text-text-secondary hover:text-text-primary hover:bg-bg-hover"
          )}
        >
          <div className="flex items-center gap-3">
            <item.icon size={20} />
            <span>{item.label}</span>
          </div>
          <ChevronDown 
            size={16} 
            className={cn(
              "transition-transform duration-fast",
              expanded && "rotate-180"
            )}
          />
        </button>
        
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="ml-4 pl-4 border-l border-border-default mt-1 space-y-1">
                {item.children.map(child => (
                  <NavLink
                    key={child.href}
                    href={child.href}
                    icon={child.icon}
                    label={child.label}
                    collapsed={false}
                    isActive={pathname === child.href}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }
  
  return (
    <NavLink 
      href={item.href}
      icon={item.icon}
      label={item.label}
      collapsed={collapsed}
      isActive={isActive}
    />
  )
}

// Base NavLink component
function NavLink({ href, icon: Icon, label, collapsed, isActive }) {
  const content = (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 px-3 py-2 rounded-md",
        "transition-colors duration-fast",
        isActive 
          ? "bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400"
          : "text-text-secondary hover:text-text-primary hover:bg-bg-hover"
      )}
    >
      <Icon size={20} />
      {!collapsed && <span>{label}</span>}
    </Link>
  )
  
  if (collapsed) {
    return (
      <Tooltip content={label} side="right">
        {content}
      </Tooltip>
    )
  }
  
  return content
}
```

---

### A0-06: Data Display Components

**Objective**: Build components for displaying data with optimal performance.

#### DataTable Component (Virtualized)

**File**: `src/components/data-display/DataTable.tsx`

```tsx
'use client'

import { useState, useMemo } from 'react'
import { 
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from '@tanstack/react-table'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Skeleton } from '@/components/ui/Skeleton'

interface DataTableProps<T> {
  data: T[]
  columns: ColumnDef<T>[]
  loading?: boolean
  pagination?: boolean
  pageSize?: number
  onRowClick?: (row: T) => void
  emptyState?: React.ReactNode
}

export function DataTable<T>({
  data,
  columns,
  loading,
  pagination = true,
  pageSize = 10,
  onRowClick,
  emptyState,
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])
  
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: pagination ? getPaginationRowModel() : undefined,
    onSortingChange: setSorting,
    state: { sorting },
    initialState: {
      pagination: { pageSize },
    },
  })
  
  if (loading) {
    return <DataTableSkeleton columns={columns.length} rows={pageSize} />
  }
  
  if (data.length === 0 && emptyState) {
    return <>{emptyState}</>
  }
  
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-border-default overflow-hidden">
        <table className="w-full">
          <thead className="bg-bg-tertiary">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    className={cn(
                      "px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider",
                      header.column.getCanSort() && "cursor-pointer select-none hover:bg-bg-hover"
                    )}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-2">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getCanSort() && (
                        <SortIcon sorted={header.column.getIsSorted()} />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-border-default bg-bg-secondary">
            {table.getRowModel().rows.map(row => (
              <tr 
                key={row.id}
                onClick={() => onRowClick?.(row.original)}
                className={cn(
                  "transition-colors duration-fast",
                  onRowClick && "cursor-pointer hover:bg-bg-hover"
                )}
              >
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-4 py-3 text-sm text-text-primary">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {pagination && <Pagination table={table} />}
    </div>
  )
}

// Skeleton loader for table
function DataTableSkeleton({ columns, rows }: { columns: number; rows: number }) {
  return (
    <div className="rounded-lg border border-border-default overflow-hidden">
      <table className="w-full">
        <thead className="bg-bg-tertiary">
          <tr>
            {Array.from({ length: columns }).map((_, i) => (
              <th key={i} className="px-4 py-3">
                <Skeleton className="h-4 w-20" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-default bg-bg-secondary">
          {Array.from({ length: rows }).map((_, rowIdx) => (
            <tr key={rowIdx}>
              {Array.from({ length: columns }).map((_, colIdx) => (
                <td key={colIdx} className="px-4 py-3">
                  <Skeleton className="h-4 w-full" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

#### StatusBadge Component

```tsx
import { cn } from '@/lib/utils'

type Status = 'active' | 'draft' | 'proposed' | 'pending' | 'deprecated' | 
              'passed' | 'warning' | 'failed' | 'running'

const statusConfig: Record<Status, { label: string; className: string }> = {
  active: { 
    label: 'Active', 
    className: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
  },
  draft: { 
    label: 'Draft', 
    className: 'bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300' 
  },
  proposed: { 
    label: 'Proposed', 
    className: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' 
  },
  pending: { 
    label: 'Pending Review', 
    className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' 
  },
  deprecated: { 
    label: 'Deprecated', 
    className: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' 
  },
  passed: { 
    label: 'Passed', 
    className: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
  },
  warning: { 
    label: 'Warning', 
    className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' 
  },
  failed: { 
    label: 'Failed', 
    className: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' 
  },
  running: { 
    label: 'Running', 
    className: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' 
  },
}

interface StatusBadgeProps {
  status: Status
  size?: 'sm' | 'md'
  showDot?: boolean
}

export function StatusBadge({ status, size = 'sm', showDot = true }: StatusBadgeProps) {
  const config = statusConfig[status]
  
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 font-medium rounded-full",
      size === 'sm' ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm",
      config.className
    )}>
      {showDot && (
        <span className={cn(
          "rounded-full",
          size === 'sm' ? "w-1.5 h-1.5" : "w-2 h-2",
          status === 'running' && "animate-pulse",
          // Dot inherits text color
          "bg-current"
        )} />
      )}
      {config.label}
    </span>
  )
}
```

---

### A0-07: Feedback Components

**Objective**: Build components for user feedback with optimal UX.

#### Toast System (Non-blocking notifications)

**File**: `src/components/feedback/Toast.tsx`

```tsx
'use client'

import { create } from 'zustand'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  type: ToastType
  title: string
  description?: string
  duration?: number
}

interface ToastStore {
  toasts: Toast[]
  add: (toast: Omit<Toast, 'id'>) => void
  remove: (id: string) => void
}

export const useToast = create<ToastStore>((set) => ({
  toasts: [],
  add: (toast) => {
    const id = Math.random().toString(36).substring(7)
    set((state) => ({ 
      toasts: [...state.toasts, { ...toast, id }] 
    }))
    
    // Auto-remove after duration
    const duration = toast.duration ?? 5000
    if (duration > 0) {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id)
        }))
      }, duration)
    }
  },
  remove: (id) => set((state) => ({
    toasts: state.toasts.filter((t) => t.id !== id)
  })),
}))

// Helper function for easy toast creation
export const toast = {
  success: (title: string, description?: string) => 
    useToast.getState().add({ type: 'success', title, description }),
  error: (title: string, description?: string) => 
    useToast.getState().add({ type: 'error', title, description }),
  warning: (title: string, description?: string) => 
    useToast.getState().add({ type: 'warning', title, description }),
  info: (title: string, description?: string) => 
    useToast.getState().add({ type: 'info', title, description }),
}

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}

const styles = {
  success: 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800',
  error: 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800',
  warning: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800',
  info: 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800',
}

const iconStyles = {
  success: 'text-green-600 dark:text-green-400',
  error: 'text-red-600 dark:text-red-400',
  warning: 'text-yellow-600 dark:text-yellow-400',
  info: 'text-blue-600 dark:text-blue-400',
}

export function ToastContainer() {
  const { toasts, remove } = useToast()
  
  return (
    <div className="fixed bottom-4 right-4 z-toast space-y-2 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => {
          const Icon = icons[toast.type]
          
          return (
            <motion.div
              key={toast.id}
              layout
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className={cn(
                "pointer-events-auto w-80 rounded-lg border p-4 shadow-lg",
                styles[toast.type]
              )}
            >
              <div className="flex items-start gap-3">
                <Icon className={cn("w-5 h-5 mt-0.5", iconStyles[toast.type])} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary">
                    {toast.title}
                  </p>
                  {toast.description && (
                    <p className="mt-1 text-sm text-text-secondary">
                      {toast.description}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => remove(toast.id)}
                  className="text-text-tertiary hover:text-text-primary transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
```

#### Loading Skeleton

```tsx
import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-bg-tertiary",
        className
      )}
    />
  )
}

// Pre-built skeleton patterns
export function CardSkeleton() {
  return (
    <div className="rounded-lg border border-border-default p-4 space-y-3">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-20" />
      </div>
    </div>
  )
}

export function TableRowSkeleton({ columns = 5 }: { columns?: number }) {
  return (
    <tr>
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  )
}
```

#### Empty State

```tsx
import { LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-12 h-12 rounded-full bg-bg-tertiary flex items-center justify-center mb-4">
        <Icon className="w-6 h-6 text-text-tertiary" />
      </div>
      <h3 className="text-lg font-medium text-text-primary mb-1">{title}</h3>
      <p className="text-sm text-text-secondary max-w-sm mb-4">{description}</p>
      {action && (
        <Button onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  )
}
```

---

### A0-08: Form Components

**Objective**: Build form primitives with excellent UX.

#### WizardStepper

```tsx
'use client'

import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Step {
  id: string
  label: string
  description?: string
}

interface WizardStepperProps {
  steps: Step[]
  currentStep: number
  onStepClick?: (step: number) => void
  allowNavigation?: boolean
}

export function WizardStepper({ 
  steps, 
  currentStep, 
  onStepClick,
  allowNavigation = false 
}: WizardStepperProps) {
  return (
    <nav aria-label="Progress" className="w-full">
      <ol className="flex items-center">
        {steps.map((step, index) => {
          const isCompleted = index < currentStep
          const isCurrent = index === currentStep
          const isClickable = allowNavigation && (isCompleted || index === currentStep + 1)
          
          return (
            <li 
              key={step.id} 
              className={cn(
                "flex items-center",
                index !== steps.length - 1 && "flex-1"
              )}
            >
              <button
                onClick={() => isClickable && onStepClick?.(index)}
                disabled={!isClickable}
                className={cn(
                  "flex items-center gap-3 group",
                  isClickable && "cursor-pointer"
                )}
              >
                {/* Step indicator */}
                <span
                  className={cn(
                    "flex items-center justify-center w-8 h-8 rounded-full border-2 transition-colors duration-fast",
                    isCompleted && "bg-primary-600 border-primary-600",
                    isCurrent && "border-primary-600 text-primary-600",
                    !isCompleted && !isCurrent && "border-border-default text-text-tertiary",
                    isClickable && !isCurrent && "group-hover:border-primary-400"
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4 text-white" />
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </span>
                
                {/* Label */}
                <span className={cn(
                  "text-sm font-medium hidden sm:block",
                  isCurrent ? "text-text-primary" : "text-text-secondary"
                )}>
                  {step.label}
                </span>
              </button>
              
              {/* Connector line */}
              {index !== steps.length - 1 && (
                <div className="flex-1 mx-4">
                  <div className="h-0.5 bg-border-default relative">
                    <motion.div
                      className="absolute inset-y-0 left-0 bg-primary-600"
                      initial={{ width: '0%' }}
                      animate={{ width: isCompleted ? '100%' : '0%' }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
```

#### FormField with validation

```tsx
import { forwardRef } from 'react'
import { useFormContext } from 'react-hook-form'
import { cn } from '@/lib/utils'
import { Input } from '@/components/ui/Input'

interface FormFieldProps {
  name: string
  label: string
  description?: string
  required?: boolean
  children?: React.ReactNode
}

export function FormField({ 
  name, 
  label, 
  description, 
  required,
  children 
}: FormFieldProps) {
  const { formState: { errors } } = useFormContext()
  const error = errors[name]
  
  return (
    <div className="space-y-2">
      <label htmlFor={name} className="block text-sm font-medium text-text-primary">
        {label}
        {required && <span className="text-error ml-1">*</span>}
      </label>
      
      {description && (
        <p className="text-sm text-text-tertiary">{description}</p>
      )}
      
      {children}
      
      {error && (
        <p className="text-sm text-error" role="alert">
          {error.message as string}
        </p>
      )}
    </div>
  )
}
```

---

### A0-09 to A0-15: Remaining Tasks

For brevity, I'll summarize the key requirements for remaining tasks:

#### A0-09: Navigation Components
- **Tabs**: Keyboard navigable, animated underline
- **Breadcrumbs**: Auto-generated from route, truncation for long paths
- **Pagination**: Page size selector, keyboard shortcuts

#### A0-10: API Client Setup
```typescript
// src/lib/api/client.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      gcTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

// Generic fetch wrapper with error handling
export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })
  
  if (!response.ok) {
    throw new ApiError(response.status, await response.json())
  }
  
  return response.json()
}
```

#### A0-11: Mock Service Worker Setup
```typescript
// src/lib/mocks/handlers.ts
import { http, HttpResponse } from 'msw'
import { contracts, assets, issues } from './data'

export const handlers = [
  // Contracts
  http.get('/api/contracts', ({ request }) => {
    const url = new URL(request.url)
    const status = url.searchParams.get('status')
    // Filter and return
    return HttpResponse.json({ data: contracts, total: contracts.length })
  }),
  
  // Add artificial delay to simulate network (remove in production)
  // http.get('/api/*', async () => {
  //   await delay(200)
  // }),
]
```

#### A0-12: Shared Hooks
- `useDebounce` - For search inputs
- `useUnsavedChanges` - Block navigation when form is dirty
- `useLocalStorage` - Persist user preferences
- `usePrefetch` - Prefetch data on hover

#### A0-13: TypeScript Types
- All entity types from specification
- API request/response types
- Form schemas with Zod

#### A0-14: Root Layout
- Providers wrapper (React Query, Theme, Toast)
- Global error boundary
- Loading states

#### A0-15: Component Documentation
- Storybook setup OR
- Documentation page at `/dev/components`

---

## Performance Optimization Guidelines

### 1. Prefetching Strategy
```tsx
// Prefetch on link hover
<Link 
  href="/studio/contracts/123"
  onMouseEnter={() => {
    queryClient.prefetchQuery({
      queryKey: ['contract', '123'],
      queryFn: () => fetchContract('123'),
    })
  }}
>
```

### 2. Optimistic Updates
```tsx
// Update UI immediately, rollback on error
const mutation = useMutation({
  mutationFn: updateContract,
  onMutate: async (newData) => {
    await queryClient.cancelQueries(['contract', id])
    const previous = queryClient.getQueryData(['contract', id])
    queryClient.setQueryData(['contract', id], newData)
    return { previous }
  },
  onError: (err, newData, context) => {
    queryClient.setQueryData(['contract', id], context.previous)
  },
})
```

### 3. Route Prefetching
```tsx
// In layout or parent component
import { useRouter } from 'next/navigation'

// Prefetch likely next routes
useEffect(() => {
  router.prefetch('/studio/contracts')
  router.prefetch('/studio/assets')
}, [])
```

### 4. Image Optimization
- Use Next.js `<Image>` component
- Specify dimensions to prevent layout shift
- Use blur placeholder for large images

### 5. Bundle Optimization
- Dynamic imports for heavy components (Monaco editor, charts)
- Code splitting by route
- Tree shaking for icon library

---

## Exit Criteria Checklist

- [ ] Project builds without errors
- [ ] All components render correctly in light/dark mode
- [ ] Theme switches instantly (no flash)
- [ ] All components are keyboard accessible
- [ ] Focus states are visible
- [ ] Loading skeletons match final layout
- [ ] Toast notifications work
- [ ] Mock API returns realistic data
- [ ] Lighthouse performance > 90
- [ ] No TypeScript errors
- [ ] Storybook/docs available for all components
