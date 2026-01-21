import { test as base, Page } from '@playwright/test'

/**
 * Test fixtures for contract E2E tests
 */

export interface TestUser {
  email: string
  password: string
  role: 'admin' | 'user' | 'viewer'
}

export const TEST_USERS: Record<string, TestUser> = {
  admin: {
    email: 'brackly@griot.com',
    password: 'melly',
    role: 'admin',
  },
}

export const TEST_DATA = {
  newContract: {
    name: 'Test Contract E2E',
    description: 'Contract created by E2E test automation',
    domain: 'analytics',
    status: 'draft' as const,
  },
  newTable: {
    name: 'test_table',
    description: 'Test table for E2E',
  },
  newField: {
    name: 'test_field',
    logicalType: 'string',
    required: true,
    primaryKey: false,
  },
}

/**
 * Login helper function
 */
export async function login(page: Page, user: TestUser = TEST_USERS.admin) {
  await page.goto('/login')
  await page.waitForLoadState('networkidle')

  await page.fill('input[name="email"]', user.email)
  await page.fill('input[name="password"]', user.password)
  await page.click('button[type="submit"]')

  // Wait for redirect
  await page.waitForURL(/\/(dashboard|studio)/, { timeout: 30000 })
}

/**
 * Extended test with authentication
 */
export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ page }, use) => {
    await login(page)
    await use(page)
  },
})

export { expect } from '@playwright/test'

/**
 * Wait for API to be ready
 */
export async function waitForAPI(page: Page) {
  await page.waitForLoadState('networkidle')
}

/**
 * Navigate to contracts list
 */
export async function goToContracts(page: Page) {
  await page.goto('/studio/contracts')
  await waitForAPI(page)
}

/**
 * Navigate to contract detail
 */
export async function goToContractDetail(page: Page, contractId: string) {
  await page.goto(`/studio/contracts/${contractId}`)
  await waitForAPI(page)
}

/**
 * Navigate to contract edit
 */
export async function goToContractEdit(page: Page, contractId: string) {
  await page.goto(`/studio/contracts/${contractId}/edit`)
  await waitForAPI(page)
}

/**
 * Navigate to contract creation wizard
 */
export async function goToContractWizard(page: Page) {
  await page.goto('/studio/contracts/new/wizard')
  await waitForAPI(page)
}

/**
 * Fill wizard step 1 (Basic Info)
 */
export async function fillWizardStep1(page: Page, data: typeof TEST_DATA.newContract) {
  await page.fill('input[placeholder*="Contract"]', data.name)
  await page.fill('textarea', data.description)

  // Select domain
  await page.click('button:has-text("Select a domain")')
  await page.click(`text=${data.domain}`)
}

/**
 * Click the Next button in wizard
 */
export async function clickWizardNext(page: Page) {
  await page.click('button:has-text("Next")')
  await waitForAPI(page)
}

/**
 * Check if element exists
 */
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  return page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)
}

/**
 * Get toast message
 */
export async function getToastMessage(page: Page): Promise<string | null> {
  const toast = page.locator('[role="alert"]').first()
  if (await toast.isVisible({ timeout: 5000 }).catch(() => false)) {
    return toast.textContent()
  }
  return null
}
