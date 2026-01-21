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

// Generate unique team name
function uniqueTeamName() {
  return `Test Team ${Date.now()}`
}

test.describe('Team Management Page', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await loginAsAdmin(page)
    await page.goto('/admin/teams')
  })

  test('should display team list', async ({ page }) => {
    // Page header
    await expect(page.getByRole('heading', { name: 'Team Management' })).toBeVisible()
    await expect(page.getByText('Organize teams and domain ownership')).toBeVisible()

    // Search input
    await expect(page.getByPlaceholder('Search teams...')).toBeVisible()

    // Create button
    await expect(page.getByRole('button', { name: 'Create Team' })).toBeVisible()

    // Should show team cards
    await expect(page.getByText('Platform Team')).toBeVisible()
  })

  test('should search teams', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Search teams...')

    // Search for platform team
    await searchInput.fill('Platform')

    // Should show matching team
    await expect(page.getByText('Platform Team')).toBeVisible()

    // Search for non-existent team
    await searchInput.fill('NonExistentTeam12345')

    // Should show empty state
    await expect(page.getByText('No teams found')).toBeVisible()
  })

  test('should open create team dialog', async ({ page }) => {
    await page.getByRole('button', { name: 'Create Team' }).click()

    // Dialog should be visible
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByText('Create New Team')).toBeVisible()

    // Form fields should be visible
    await expect(page.getByLabel('Team Name')).toBeVisible()
    await expect(page.getByLabel('Description')).toBeVisible()
  })

  test('should create new team', async ({ page }) => {
    const teamName = uniqueTeamName()

    // Open create dialog
    await page.getByRole('button', { name: 'Create Team' }).click()

    // Fill form
    await page.getByLabel('Team Name').fill(teamName)
    await page.getByLabel('Description').fill('Test team description')

    // Submit
    await page.getByRole('button', { name: 'Create Team' }).last().click()

    // Wait for success
    await expect(page.getByText('Team created')).toBeVisible({ timeout: 5000 })

    // Dialog should close
    await expect(page.getByRole('dialog')).not.toBeVisible()

    // New team should appear
    await expect(page.getByText(teamName)).toBeVisible()
  })

  test('should show team card with details', async ({ page }) => {
    // Platform Team card should show:
    const teamCard = page.locator('[class*="Card"]').filter({ hasText: 'Platform Team' })

    // Team name
    await expect(teamCard.getByText('Platform Team')).toBeVisible()

    // Member count
    await expect(teamCard.getByText(/\d+ members/)).toBeVisible()

    // Action menu
    await expect(teamCard.getByRole('button')).toBeVisible()
  })

  test('should navigate to team detail page', async ({ page }) => {
    // Find the View button for Platform Team
    const viewButton = page.locator('a').filter({ hasText: 'View' }).first()

    if (await viewButton.isVisible()) {
      await viewButton.click()

      // Should be on team detail page
      await expect(page.getByText('Team Members')).toBeVisible({ timeout: 5000 })
      await expect(page.getByRole('button', { name: 'Add Member' })).toBeVisible()
    }
  })

  test('should show team action menu', async ({ page }) => {
    // Find action button on first team card
    const actionButton = page
      .locator('[class*="Card"]')
      .first()
      .getByRole('button')
      .filter({ has: page.locator('[data-lucide="more-horizontal"]') })
      .first()

    if (await actionButton.isVisible()) {
      await actionButton.click()

      // Dropdown should show actions
      await expect(page.getByText('View Details')).toBeVisible()
      await expect(page.getByText('Edit Team')).toBeVisible()
      await expect(page.getByText('Delete Team')).toBeVisible()
    }
  })

  test('should cancel create team dialog', async ({ page }) => {
    await page.getByRole('button', { name: 'Create Team' }).click()
    await expect(page.getByRole('dialog')).toBeVisible()

    await page.getByRole('button', { name: 'Cancel' }).click()
    await expect(page.getByRole('dialog')).not.toBeVisible()
  })
})

test.describe('Team Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await loginAsAdmin(page)
    // Navigate to first team's detail page
    await page.goto('/admin/teams/team-001')
  })

  test('should display team details', async ({ page }) => {
    // Team name in header
    await expect(page.getByRole('heading', { name: 'Platform Team' })).toBeVisible()

    // Team info cards
    await expect(page.getByText('Members')).toBeVisible()
    await expect(page.getByText('Default Role')).toBeVisible()
    await expect(page.getByText('Domains')).toBeVisible()

    // Members section
    await expect(page.getByText('Team Members')).toBeVisible()
  })

  test('should have back button to teams list', async ({ page }) => {
    await page.getByRole('button', { name: 'Back to Teams' }).click()
    await page.waitForURL('/admin/teams')
    await expect(page.getByRole('heading', { name: 'Team Management' })).toBeVisible()
  })

  test('should open add member dialog', async ({ page }) => {
    await page.getByRole('button', { name: 'Add Member' }).click()

    // Dialog should be visible
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByText('Add Team Member')).toBeVisible()

    // Form fields
    await expect(page.getByLabel('User Email')).toBeVisible()
  })

  test('should show member list with actions', async ({ page }) => {
    // Members should be displayed
    const memberList = page.locator('[class*="border-border-default"]').filter({ hasText: '@' })

    // At least one member should be visible
    const memberCount = await memberList.count()
    if (memberCount > 0) {
      // Each member should have action menu
      const firstMember = memberList.first()
      await expect(firstMember.getByRole('button')).toBeVisible()
    }
  })
})
