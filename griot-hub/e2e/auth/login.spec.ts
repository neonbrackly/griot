import { test, expect, type Page } from '@playwright/test'

// Test credentials
const ADMIN_EMAIL = 'brackly@griot.com'
const ADMIN_PASSWORD = 'melly'
const INVALID_EMAIL = 'invalid@example.com'
const INVALID_PASSWORD = 'wrongpassword'

// Helper function to clear auth state
async function clearAuthState(page: Page) {
  await page.evaluate(() => localStorage.removeItem('griot_auth'))
}

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await page.goto('/login')
  })

  test('should display login form with all elements', async ({ page }) => {
    // Check page title and description
    await expect(page.getByRole('heading', { name: 'Welcome to Griot' })).toBeVisible()
    await expect(page.getByText('Sign in to your account')).toBeVisible()

    // Check form fields
    await expect(page.getByLabel('Email')).toBeVisible()
    await expect(page.getByLabel('Password')).toBeVisible()
    await expect(page.getByText('Remember me for 30 days')).toBeVisible()

    // Check buttons
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible()
    await expect(page.getByText('Forgot password?')).toBeVisible()

    // Check OAuth buttons (3 buttons for Google, Microsoft, SSO)
    const oauthButtons = page.locator('button[type="button"]')
    await expect(oauthButtons).toHaveCount(3)

    // Check signup link
    await expect(page.getByText("Don't have an account?")).toBeVisible()
    await expect(page.getByRole('link', { name: 'Sign up' })).toBeVisible()

    // Check demo hint
    await expect(page.getByText('brackly@griot.com')).toBeVisible()
  })

  test('should show validation errors for empty fields', async ({ page }) => {
    // Click submit without entering anything
    await page.getByRole('button', { name: 'Sign In' }).click()

    // Should show validation errors
    await expect(page.getByText('Please enter a valid email address')).toBeVisible()
    await expect(page.getByText('Password is required')).toBeVisible()
  })

  test('should show validation error for invalid email format', async ({ page }) => {
    await page.getByLabel('Email').fill('notanemail')
    await page.getByLabel('Password').fill('password')
    await page.getByRole('button', { name: 'Sign In' }).click()

    await expect(page.getByText('Please enter a valid email address')).toBeVisible()
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.getByLabel('Email').fill(INVALID_EMAIL)
    await page.getByLabel('Password').fill(INVALID_PASSWORD)
    await page.getByRole('button', { name: 'Sign In' }).click()

    // Wait for error toast
    await expect(page.getByText('Login failed')).toBeVisible({ timeout: 5000 })
    await expect(page.getByText('Invalid email or password')).toBeVisible()
  })

  test('should toggle password visibility', async ({ page }) => {
    const passwordInput = page.getByLabel('Password')
    const toggleButton = page.locator('[type="button"]').filter({ has: page.locator('[data-lucide="eye"]') })

    // Initially password should be hidden
    await expect(passwordInput).toHaveAttribute('type', 'password')

    // Click toggle to show password
    await page.getByLabel('Password').fill('testpassword')

    // Find the eye toggle button in the password input wrapper
    const eyeButton = page.locator('input[type="password"] + div button, input[id="password"] ~ div button').first()
    if (await eyeButton.isVisible()) {
      await eyeButton.click()
      await expect(passwordInput).toHaveAttribute('type', 'text')
    }
  })

  test('should login successfully with admin credentials', async ({ page }) => {
    await page.getByLabel('Email').fill(ADMIN_EMAIL)
    await page.getByLabel('Password').fill(ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Sign In' }).click()

    // Should redirect to dashboard
    await page.waitForURL('/', { timeout: 10000 })

    // Should see user info in top nav
    await expect(page.getByText('Brackly Murunga')).toBeVisible()
  })

  test('should persist login state across page reload', async ({ page }) => {
    // Login
    await page.getByLabel('Email').fill(ADMIN_EMAIL)
    await page.getByLabel('Password').fill(ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Sign In' }).click()
    await page.waitForURL('/', { timeout: 10000 })

    // Reload page
    await page.reload()

    // Should still be logged in
    await expect(page.getByText('Brackly Murunga')).toBeVisible()
  })

  test('should navigate to forgot password page', async ({ page }) => {
    await page.getByText('Forgot password?').click()
    await page.waitForURL('/forgot-password')
    await expect(page.getByRole('heading', { name: 'Forgot your password?' })).toBeVisible()
  })

  test('should navigate to signup page', async ({ page }) => {
    await page.getByRole('link', { name: 'Sign up' }).click()
    await page.waitForURL('/signup')
    await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible()
  })

  test('should redirect authenticated users to dashboard', async ({ page }) => {
    // Login first
    await page.getByLabel('Email').fill(ADMIN_EMAIL)
    await page.getByLabel('Password').fill(ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Sign In' }).click()
    await page.waitForURL('/', { timeout: 10000 })

    // Try to go back to login
    await page.goto('/login')

    // Should be redirected back to dashboard
    await page.waitForURL('/', { timeout: 5000 })
  })
})

test.describe('Logout Flow', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthState(page)
    await page.goto('/login')
    // Login first
    await page.getByLabel('Email').fill(ADMIN_EMAIL)
    await page.getByLabel('Password').fill(ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Sign In' }).click()
    await page.waitForURL('/', { timeout: 10000 })
  })

  test('should logout successfully', async ({ page }) => {
    // Click on user menu
    await page.getByText('Brackly Murunga').click()

    // Click logout
    await page.getByText('Sign Out').click()

    // Should redirect to login page
    await page.waitForURL('/login', { timeout: 5000 })
  })

  test('should clear auth state on logout', async ({ page }) => {
    // Click on user menu
    await page.getByText('Brackly Murunga').click()
    await page.getByText('Sign Out').click()
    await page.waitForURL('/login', { timeout: 5000 })

    // Try to navigate to dashboard
    await page.goto('/')

    // Should be redirected back to login
    await page.waitForURL('/login', { timeout: 5000 })
  })
})
