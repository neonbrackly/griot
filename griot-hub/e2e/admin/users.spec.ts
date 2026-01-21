import { test, expect, type Page } from '@playwright/test'

// Test credentials
const ADMIN_EMAIL = 'brackly@griot.com'
const ADMIN_PASSWORD = 'melly'

// Helper function to clear auth state
async function clearAuthState(page: Page) {
  await page.evaluate(() => localStorage.removeItem('griot_auth'))
}

// Helper to login as admin
async function loginAsAdmin(page: Page) {
  await page.goto('/login')
  await page.getByLabel('Email').fill(ADMIN_EMAIL)
  await page.getByLabel('Password').fill(ADMIN_PASSWORD)
  await page.getByRole('button', { name: 'Sign In' }).click()
  await page.waitForURL('/', { timeout: 10000 })
}

// Generate unique email for invites
function uniqueEmail() {
  return `invite${Date.now()}@example.com`
}

test.describe('User Management Page', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await loginAsAdmin(page)
    await page.goto('/admin/users')
  })

  test('should display user list', async ({ page }) => {
    // Page header
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible()

    // Search input
    await expect(page.getByPlaceholder('Search users...')).toBeVisible()

    // Role filter
    await expect(page.getByText('All Roles')).toBeVisible()

    // Invite button
    await expect(page.getByRole('button', { name: 'Invite User' })).toBeVisible()

    // Data table should be visible
    await expect(page.locator('table')).toBeVisible()
  })

  test('should search users by name or email', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Search users...')

    // Search for admin user
    await searchInput.fill('brackly')
    await page.waitForTimeout(500) // Wait for debounce

    // Should show matching user
    await expect(page.getByText('brackly@griot.com')).toBeVisible()
  })

  test('should filter users by role', async ({ page }) => {
    // Click role filter
    await page.getByText('All Roles').click()

    // Select Admin role
    await page.getByRole('option', { name: 'Admin' }).click()

    // Wait for filter to apply
    await page.waitForTimeout(500)

    // Should show admin users
    await expect(page.getByText('brackly@griot.com')).toBeVisible()
  })

  test('should open invite user dialog', async ({ page }) => {
    await page.getByRole('button', { name: 'Invite User' }).click()

    // Dialog should be visible
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByText('Invite New User')).toBeVisible()

    // Form fields should be visible
    await expect(page.getByLabel('Full Name')).toBeVisible()
    await expect(page.getByLabel('Email Address')).toBeVisible()
    await expect(page.getByLabel('Role')).toBeVisible()
    await expect(page.getByLabel('Team')).toBeVisible()
  })

  test('should invite new user', async ({ page }) => {
    const inviteEmail = uniqueEmail()

    // Open invite dialog
    await page.getByRole('button', { name: 'Invite User' }).click()

    // Fill form
    await page.getByLabel('Full Name').fill('Test Invite User')
    await page.getByLabel('Email Address').fill(inviteEmail)

    // Select role
    await page.locator('[data-value="member"]').click()

    // Select team (first available)
    await page.getByLabel('Team').click()
    await page.getByRole('option').first().click()

    // Submit
    await page.getByRole('button', { name: 'Send Invitation' }).click()

    // Wait for success
    await expect(page.getByText('Invitation sent')).toBeVisible({ timeout: 5000 })

    // Dialog should close
    await expect(page.getByRole('dialog')).not.toBeVisible()
  })

  test('should show user action menu', async ({ page }) => {
    // Find action button in the first row (excluding header)
    const actionButton = page.locator('table tbody tr').first().getByRole('button').last()
    await actionButton.click()

    // Dropdown should show actions
    await expect(page.getByText('Change Role')).toBeVisible()
    await expect(page.getByText('Reset Password')).toBeVisible()
    await expect(page.getByText('Deactivate User')).toBeVisible()
  })

  test('should cancel invite dialog', async ({ page }) => {
    await page.getByRole('button', { name: 'Invite User' }).click()
    await expect(page.getByRole('dialog')).toBeVisible()

    await page.getByRole('button', { name: 'Cancel' }).click()
    await expect(page.getByRole('dialog')).not.toBeVisible()
  })
})
