# QA, Testing & Polish Agent

## Mission Statement
Ensure the entire application works flawlessly. Write comprehensive Playwright tests, perform visual regression testing, fix bugs, and polish the UI/UX to perfection. You are the last line of defense before release.

---

## Feature Ownership

### Core Responsibilities
1. **E2E Testing** - Playwright tests for all critical user flows
2. **Visual Regression** - Screenshot comparison testing
3. **Accessibility Testing** - WCAG 2.1 AA compliance
4. **Performance Testing** - Lighthouse audits
5. **Cross-Browser Testing** - Chrome, Firefox, Safari
6. **Bug Fixes** - Fix issues found during testing
7. **UI Polish** - Consistency, animations, micro-interactions

### Files Owned

```
/
├── tests/
│   ├── e2e/
│   │   ├── dashboard.spec.ts          # Dashboard tests
│   │   ├── contracts/
│   │   │   ├── list.spec.ts           # Contract list tests
│   │   │   ├── detail.spec.ts         # Contract detail tests
│   │   │   ├── create-wizard.spec.ts  # Wizard flow tests
│   │   │   └── yaml-import.spec.ts    # YAML editor tests
│   │   ├── assets/
│   │   │   ├── list.spec.ts           # Asset list tests
│   │   │   ├── detail.spec.ts         # Asset detail tests
│   │   │   └── create-wizard.spec.ts  # Asset wizard tests
│   │   ├── issues/
│   │   │   ├── list.spec.ts           # Issues list tests
│   │   │   └── detail.spec.ts         # Issue detail tests
│   │   ├── tasks.spec.ts              # My Tasks tests
│   │   ├── reports.spec.ts            # Reports tests
│   │   ├── marketplace.spec.ts        # Marketplace tests
│   │   ├── admin/
│   │   │   ├── users.spec.ts          # User management tests
│   │   │   └── teams.spec.ts          # Team management tests
│   │   ├── settings.spec.ts           # Settings tests
│   │   └── navigation.spec.ts         # Global navigation tests
│   ├── visual/
│   │   ├── screenshots/               # Baseline screenshots
│   │   └── visual-regression.spec.ts  # Visual comparison tests
│   ├── accessibility/
│   │   └── a11y.spec.ts               # Accessibility tests
│   ├── performance/
│   │   └── lighthouse.spec.ts         # Performance audits
│   └── utils/
│       └── test-helpers.ts            # Shared test utilities
├── playwright.config.ts               # Playwright configuration
└── test-results/                      # Test output artifacts
```

---

## Technical Specifications

### Quality Metrics
| Metric | Target |
|--------|--------|
| Test Coverage | > 80% of critical paths |
| Visual Regression | 0 unintended changes |
| Accessibility | WCAG 2.1 AA compliant |
| Performance | Lighthouse > 90 |
| Cross-browser | Chrome, Firefox, Safari |
| Responsive | Mobile, Tablet, Desktop |

### Playwright Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
  ],

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 12'] } },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### Test Utilities
```typescript
// tests/utils/test-helpers.ts
import { Page, expect } from '@playwright/test'

export class TestHelpers {
  constructor(private page: Page) {}

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle')
    await expect(this.page.locator('[data-loading="true"]')).toHaveCount(0)
    await expect(this.page.locator('.animate-pulse')).toHaveCount(0)
  }

  async navigateTo(path: string) {
    await this.page.goto(path)
    await this.waitForPageLoad()
  }

  async fillField(label: string, value: string) {
    await this.page.getByLabel(label).fill(value)
  }

  async clickButton(text: string) {
    await this.page.getByRole('button', { name: text }).click()
  }

  async expectToast(message: string) {
    await expect(this.page.getByText(message)).toBeVisible()
  }

  async expectURL(path: string) {
    await expect(this.page).toHaveURL(new RegExp(path))
  }
}
```

---

## Test Categories

### Critical Path Tests (Priority 1)
These flows MUST work perfectly:

1. **Dashboard Load**
   - Health scores display
   - Timeline renders
   - Active issues show
   - Generate Report works

2. **Contract CRUD**
   - List contracts with filters
   - View contract detail
   - Create contract via wizard (all steps)
   - Submit for approval
   - Approve/Reject flow

3. **Asset CRUD**
   - List assets with filters
   - View asset detail
   - Create asset via wizard (all steps)
   - Sync schema

4. **Navigation**
   - Sidebar navigation
   - Global search (Cmd+K)
   - Breadcrumbs
   - URL state persistence

### Secondary Path Tests (Priority 2)
1. Issues management flow
2. My Tasks workflows
3. Reports generation
4. Marketplace browsing
5. Settings updates
6. Admin user/team management

### Visual Regression Tests
- Dashboard (light + dark)
- Contract list (empty, populated)
- Contract detail
- Asset detail
- Wizard steps (all)
- Admin pages
- Mobile responsive views

### Accessibility Tests
```typescript
// tests/accessibility/a11y.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  test('dashboard has no violations', async ({ page }) => {
    await page.goto('/')
    const results = await new AxeBuilder({ page }).analyze()
    expect(results.violations).toEqual([])
  })

  // Test all major pages...
})
```

---

## Test Scripts

### npm Scripts
```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:headed": "playwright test --headed",
    "test:visual": "playwright test tests/visual",
    "test:a11y": "playwright test tests/accessibility",
    "test:perf": "playwright test tests/performance"
  }
}
```

---

## Bug Tracking

### Bug Report Format
When documenting bugs, use this format:

```markdown
## Bug: [Short Description]

**Severity:** Critical / High / Medium / Low
**Page:** /path/to/page
**Browser:** Chrome / Firefox / Safari / All

### Steps to Reproduce
1. Navigate to X
2. Click on Y
3. Observe Z

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Screenshot/Recording
[Attach if applicable]

### Fix Applied
[Description of fix, file paths changed]
```

---

## Polish Checklist

### Visual Polish
- [ ] Consistent spacing (4px grid)
- [ ] Proper typography hierarchy
- [ ] Loading states for all async operations
- [ ] Empty states with helpful messaging
- [ ] Error states with recovery options
- [ ] Hover states on all interactive elements
- [ ] Focus visible on keyboard navigation
- [ ] Smooth transitions (150-300ms)
- [ ] Dark mode complete coverage

### Interaction Polish
- [ ] No layout shift during loading
- [ ] Optimistic updates where applicable
- [ ] Form validation feedback
- [ ] Confirm dialogs for destructive actions
- [ ] Toast notifications for actions
- [ ] Keyboard shortcuts work
- [ ] Mobile touch targets (44x44px minimum)

### Performance Polish
- [ ] Debounced search inputs
- [ ] Prefetching on hover
- [ ] Code splitting for heavy components
- [ ] Image optimization
- [ ] No unnecessary re-renders

---

## Dependencies

### Provides To Other Agents
- Bug reports with fix requirements
- Test coverage reports
- Performance audit results
- Polish recommendations

### Depends On
- All Agents: Need completed features to test
- Design Agent: Test utilities setup

---

## Code References

### Key Files
| Purpose | Path |
|---------|------|
| Playwright config | `playwright.config.ts` |
| E2E tests | `tests/e2e/*.spec.ts` |
| Test helpers | `tests/utils/test-helpers.ts` |
| Visual tests | `tests/visual/*.spec.ts` |
| A11y tests | `tests/accessibility/*.spec.ts` |
| Test results | `test-results/` |
