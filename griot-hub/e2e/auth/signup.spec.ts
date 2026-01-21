import { test, expect, type Page } from '@playwright/test'

// Helper function to clear auth state
async function clearAuthState(page: Page) {
  await page.evaluate(() => localStorage.removeItem('griot_auth'))
}

// Generate unique email for each test run
function uniqueEmail() {
  return `test${Date.now()}@example.com`
}

test.describe('Signup Page', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await page.goto('/signup')
  })

  test('should display signup form with all elements', async ({ page }) => {
    // Check page title
    await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible()
    await expect(page.getByText('Get started with Griot today')).toBeVisible()

    // Check form fields
    await expect(page.getByLabel('Full Name')).toBeVisible()
    await expect(page.getByLabel('Email')).toBeVisible()
    await expect(page.getByLabel('Password', { exact: true })).toBeVisible()
    await expect(page.getByLabel('Confirm Password')).toBeVisible()

    // Check terms checkbox
    await expect(page.getByText('I agree to the')).toBeVisible()
    await expect(page.getByText('Terms of Service')).toBeVisible()

    // Check submit button
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible()

    // Check login link
    await expect(page.getByText('Already have an account?')).toBeVisible()
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible()
  })

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.getByRole('button', { name: 'Create Account' }).click()

    // Should show validation errors
    await expect(page.getByText('Name must be at least 2 characters')).toBeVisible()
    await expect(page.getByText('Please enter a valid email address')).toBeVisible()
    await expect(page.getByText('Password must be at least 8 characters')).toBeVisible()
  })

  test('should show password strength indicator', async ({ page }) => {
    // Type a weak password
    await page.getByLabel('Password', { exact: true }).fill('abc')
    await expect(page.getByText('weak', { exact: true })).toBeVisible()

    // Type a medium password
    await page.getByLabel('Password', { exact: true }).fill('Abcd1234')
    await expect(page.getByText('medium')).toBeVisible()

    // Type a strong password
    await page.getByLabel('Password', { exact: true }).fill('Abcd1234!')
    await expect(page.getByText('strong')).toBeVisible()
  })

  test('should show password requirements checklist', async ({ page }) => {
    await page.getByLabel('Password', { exact: true }).fill('A')

    // Check that requirements are shown
    await expect(page.getByText('At least 8 characters')).toBeVisible()
    await expect(page.getByText('Contains uppercase letter')).toBeVisible()
    await expect(page.getByText('Contains lowercase letter')).toBeVisible()
    await expect(page.getByText('Contains number')).toBeVisible()
    await expect(page.getByText('Contains special character')).toBeVisible()
  })

  test('should show error when passwords do not match', async ({ page }) => {
    await page.getByLabel('Full Name').fill('Test User')
    await page.getByLabel('Email').fill(uniqueEmail())
    await page.getByLabel('Password', { exact: true }).fill('Password123!')
    await page.getByLabel('Confirm Password').fill('DifferentPassword123!')
    await page.locator('#acceptTerms').check()
    await page.getByRole('button', { name: 'Create Account' }).click()

    await expect(page.getByText('Passwords do not match')).toBeVisible()
  })

  test('should require accepting terms', async ({ page }) => {
    await page.getByLabel('Full Name').fill('Test User')
    await page.getByLabel('Email').fill(uniqueEmail())
    await page.getByLabel('Password', { exact: true }).fill('Password123!')
    await page.getByLabel('Confirm Password').fill('Password123!')
    // Don't check terms
    await page.getByRole('button', { name: 'Create Account' }).click()

    await expect(page.getByText('You must accept the terms and conditions')).toBeVisible()
  })

  test('should toggle password visibility', async ({ page }) => {
    const passwordInput = page.getByLabel('Password', { exact: true })
    await passwordInput.fill('testpassword')

    // Find the visibility toggle button
    const eyeButtons = page.locator('button').filter({ has: page.locator('svg') })
    // Password input should initially be hidden
    await expect(passwordInput).toHaveAttribute('type', 'password')
  })

  test('should signup successfully with valid data', async ({ page }) => {
    const email = uniqueEmail()

    await page.getByLabel('Full Name').fill('New Test User')
    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password', { exact: true }).fill('SecurePassword123!')
    await page.getByLabel('Confirm Password').fill('SecurePassword123!')
    await page.locator('#acceptTerms').check()
    await page.getByRole('button', { name: 'Create Account' }).click()

    // Should redirect to dashboard
    await page.waitForURL('/', { timeout: 10000 })

    // Should see user name in top nav
    await expect(page.getByText('New Test User')).toBeVisible()
  })

  test('should show error for existing email', async ({ page }) => {
    // Try to signup with existing admin email
    await page.getByLabel('Full Name').fill('Test User')
    await page.getByLabel('Email').fill('brackly@griot.com')
    await page.getByLabel('Password', { exact: true }).fill('Password123!')
    await page.getByLabel('Confirm Password').fill('Password123!')
    await page.locator('#acceptTerms').check()
    await page.getByRole('button', { name: 'Create Account' }).click()

    // Should show error
    await expect(page.getByText('Signup failed')).toBeVisible({ timeout: 5000 })
    await expect(page.getByText('already exists')).toBeVisible()
  })

  test('should navigate to login page', async ({ page }) => {
    await page.getByRole('link', { name: 'Sign in' }).click()
    await page.waitForURL('/login')
    await expect(page.getByRole('heading', { name: 'Welcome to Griot' })).toBeVisible()
  })
})
