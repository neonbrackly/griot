# Agent 5: QA, Testing & Polish

## Mission Statement
Ensure the entire application works flawlessly. Write comprehensive Playwright tests, perform visual regression testing, fix bugs, and polish the UI/UX to perfection. You are the last line of defense before release.

---

## Critical Quality Metrics

| Metric | Target |
|--------|--------|
| Test Coverage | > 80% of critical paths |
| Visual Regression | 0 unintended changes |
| Accessibility | WCAG 2.1 AA compliant |
| Performance | Lighthouse > 90 |
| Cross-browser | Chrome, Firefox, Safari |
| Responsive | Mobile, Tablet, Desktop |

---

## Testing Structure

```
/tests/
├── e2e/
│   ├── dashboard.spec.ts
│   ├── contracts/
│   │   ├── list.spec.ts
│   │   ├── detail.spec.ts
│   │   ├── create-wizard.spec.ts
│   │   └── yaml-import.spec.ts
│   ├── assets/
│   │   ├── list.spec.ts
│   │   ├── detail.spec.ts
│   │   └── create-wizard.spec.ts
│   ├── issues/
│   │   ├── list.spec.ts
│   │   └── detail.spec.ts
│   ├── tasks.spec.ts
│   ├── reports.spec.ts
│   ├── marketplace.spec.ts
│   ├── admin/
│   │   ├── users.spec.ts
│   │   └── teams.spec.ts
│   ├── settings.spec.ts
│   └── navigation.spec.ts
├── visual/
│   ├── screenshots/
│   └── visual-regression.spec.ts
├── accessibility/
│   └── a11y.spec.ts
└── performance/
    └── lighthouse.spec.ts
```

---

## Task Specifications

### A5-01: Playwright Setup

**File**: `playwright.config.ts`

```typescript
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
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

**Test Utilities**: `tests/utils/test-helpers.ts`

```typescript
import { Page, expect } from '@playwright/test'

export class TestHelpers {
  constructor(private page: Page) {}
  
  // Wait for page to be fully loaded (no spinners, skeletons)
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle')
    await expect(this.page.locator('[data-loading="true"]')).toHaveCount(0)
    await expect(this.page.locator('.animate-pulse')).toHaveCount(0)
  }
  
  // Navigate and wait for load
  async navigateTo(path: string) {
    await this.page.goto(path)
    await this.waitForPageLoad()
  }
  
  // Fill form field
  async fillField(label: string, value: string) {
    await this.page.getByLabel(label).fill(value)
  }
  
  // Click button by text
  async clickButton(text: string) {
    await this.page.getByRole('button', { name: text }).click()
  }
  
  // Assert toast message
  async expectToast(message: string) {
    await expect(this.page.getByText(message)).toBeVisible()
  }
  
  // Assert URL
  async expectURL(path: string) {
    await expect(this.page).toHaveURL(new RegExp(path))
  }
}
```

---

### A5-02: Dashboard E2E Tests

**File**: `tests/e2e/dashboard.spec.ts`

```typescript
import { test, expect } from '@playwright/test'
import { TestHelpers } from '../utils/test-helpers'

test.describe('Dashboard', () => {
  let helpers: TestHelpers
  
  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page)
    await helpers.navigateTo('/')
  })
  
  test('displays health score cards', async ({ page }) => {
    // All three health cards should be visible
    await expect(page.getByText('Compliance Health')).toBeVisible()
    await expect(page.getByText('Cost Health')).toBeVisible()
    await expect(page.getByText('Analytics Health')).toBeVisible()
    
    // Scores should be numbers
    const complianceScore = page.locator('[data-testid="compliance-score"]')
    await expect(complianceScore).toHaveText(/%$/)
  })
  
  test('displays contract runs timeline', async ({ page }) => {
    await expect(page.getByText('Contract Runs')).toBeVisible()
    
    // Timeline bars should be present
    const timelineBars = page.locator('[data-testid="timeline-bar"]')
    await expect(timelineBars).toHaveCount(30) // Default 30 days
  })
  
  test('clicking timeline day navigates to run details', async ({ page }) => {
    // Click a specific day
    await page.locator('[data-testid="timeline-bar"]').first().click()
    
    // Should navigate to runs page
    await helpers.expectURL('/runs/')
  })
  
  test('displays active issues panel', async ({ page }) => {
    await expect(page.getByText('Active Issues')).toBeVisible()
    
    // Should show issue count
    const issueCount = page.locator('[data-testid="issue-count"]')
    await expect(issueCount).toBeVisible()
  })
  
  test('clicking issue navigates to issue detail', async ({ page }) => {
    // Click first issue
    await page.locator('[data-testid="issue-card"]').first().click()
    
    // Should navigate to issue detail
    await helpers.expectURL('/studio/issues/')
  })
  
  test('generate report dropdown works', async ({ page }) => {
    // Click generate report
    await page.getByRole('button', { name: 'Generate Report' }).click()
    
    // Dropdown should show report options
    await expect(page.getByText('Audit Readiness')).toBeVisible()
    await expect(page.getByText('Cost Readiness')).toBeVisible()
    await expect(page.getByText('Analytics Readiness')).toBeVisible()
    await expect(page.getByText('AI Readiness')).toBeVisible()
  })
  
  test('handles empty state gracefully', async ({ page }) => {
    // Mock empty data scenario
    await page.route('**/api/dashboard/**', async route => {
      await route.fulfill({ json: { data: [] } })
    })
    
    await page.reload()
    await helpers.waitForPageLoad()
    
    // Should show empty states, not errors
    await expect(page.getByText('error')).not.toBeVisible()
  })
})
```

---

### A5-03: Contract List E2E Tests

**File**: `tests/e2e/contracts/list.spec.