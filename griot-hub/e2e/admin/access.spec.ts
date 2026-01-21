import { test, expect, type Page } from '@playwright/test'

// Test credentials
const ADMIN_EMAIL = 'brackly@griot.com'
const ADMIN_PASSWORD = 'melly'
const VIEWER_EMAIL = 'viewer@griot.com'
const VIEWER_PASSWORD = 'password123'

// Helper function to clear auth state
async function clearAuthState(page: Page) {
  await page.evaluate(() => localStorage.removeItem('griot_auth'))
}

// Helper to login
async function login(page: Page, email: string, password: string) {
  await page.goto('/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: 'Sign In' }).click()
  await page.waitForURL('/', { timeout: 10000 })
}

test.describe('Admin Access Control', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
  })

  test('admin user should see Admin link in sidebar', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    // Admin link should be visible in sidebar
    await expect(page.getByRole('link', { name: 'Admin' })).toBeVisible()
  })

  test('viewer user should NOT see Admin link in sidebar', async ({ page }) => {
    await login(page, VIEWER_EMAIL, VIEWER_PASSWORD)

    // Admin link should NOT be visible
    await expect(page.getByRole('link', { name: 'Admin' })).not.toBeVisible()
  })

  test('admin user should access admin dashboard', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    // Click on Admin link
    await page.getByRole('link', { name: 'Admin' }).click()
    await page.waitForURL('/admin')

    // Should see admin page content
    await expect(page.getByRole('heading', { name: 'Administration' })).toBeVisible()
    await expect(page.getByText('Manage users, teams, and system settings')).toBeVisible()

    // Should see metric cards
    await expect(page.getByText('Total Users')).toBeVisible()
    await expect(page.getByText('Teams')).toBeVisible()
    await expect(page.getByText('Roles')).toBeVisible()
  })

  test('admin user should access user management page', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    await page.goto('/admin/users')

    // Should see user management page
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Invite User' })).toBeVisible()

    // Should see search and filter options
    await expect(page.getByPlaceholder('Search users...')).toBeVisible()
  })

  test('admin user should access team management page', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    await page.goto('/admin/teams')

    // Should see team management page
    await expect(page.getByRole('heading', { name: 'Team Management' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create Team' })).toBeVisible()
  })

  test('admin user should access roles page', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    await page.goto('/admin/roles')

    // Should see roles page
    await expect(page.getByRole('heading', { name: 'Roles & Permissions' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create Role' })).toBeVisible()

    // Should see permission matrix
    await expect(page.getByText('Permission Matrix')).toBeVisible()
  })
})

test.describe('Admin Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
  })

  test('should navigate between admin pages via cards', async ({ page }) => {
    await page.goto('/admin')

    // Click User Management card
    await page.getByText('User Management').click()
    await page.waitForURL('/admin/users')
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible()

    // Go back to admin
    await page.goto('/admin')

    // Click Team Management card
    await page.getByText('Team Management').click()
    await page.waitForURL('/admin/teams')
    await expect(page.getByRole('heading', { name: 'Team Management' })).toBeVisible()

    // Go back to admin
    await page.goto('/admin')

    // Click Roles card
    await page.getByText('Roles & Permissions').click()
    await page.waitForURL('/admin/roles')
    await expect(page.getByRole('heading', { name: 'Roles & Permissions' })).toBeVisible()
  })

  test('should use breadcrumbs for navigation', async ({ page }) => {
    await page.goto('/admin/users')

    // Click on Administration breadcrumb
    await page.getByRole('link', { name: 'Administration' }).click()
    await page.waitForURL('/admin')
    await expect(page.getByRole('heading', { name: 'Administration' })).toBeVisible()
  })
})

test.describe('Three-Click Rule Verification', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
  })

  test('user management page reachable in 2 clicks from dashboard', async ({ page }) => {
    // Start from dashboard
    await page.goto('/')

    // Click 1: Admin link in sidebar
    await page.getByRole('link', { name: 'Admin' }).click()

    // Click 2: User Management card
    await page.getByText('User Management').click()

    await page.waitForURL('/admin/users')
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible()
  })

  test('team detail page reachable in 3 clicks from dashboard', async ({ page }) => {
    await page.goto('/')

    // Click 1: Admin
    await page.getByRole('link', { name: 'Admin' }).click()

    // Click 2: Team Management
    await page.getByText('Team Management').click()
    await page.waitForURL('/admin/teams')

    // Click 3: First team's View button
    const viewButton = page.getByRole('button', { name: 'View' }).first()
    if (await viewButton.isVisible()) {
      await viewButton.click()
      await expect(page.getByText('Team Members')).toBeVisible({ timeout: 5000 })
    }
  })
})
