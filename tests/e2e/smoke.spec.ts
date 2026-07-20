import { expect, test } from '@playwright/test'

const BACKEND_URL = process.env.PLAYWRIGHT_BACKEND_URL ?? 'http://localhost:8000'

// This suite drives one real, shared backend (not sandboxed per test like
// the unit/integration suites) — the onboarding test below temporarily
// flips a global setting (onboarding_complete) that every other test's
// page loads depend on. `fullyParallel` (playwright.config.ts) would let
// that overlap with concurrent tests hitting `/`/`/settings` and see the
// onboarding wizard instead of the page they expected. Serial execution
// for this one file removes the race entirely.
test.describe.configure({ mode: 'serial' })

test('dashboard loads and shows backend health status using the configured app name', async ({
  page,
}) => {
  await page.goto('/')

  const status = page.getByRole('status')
  await expect(status).toContainText(/backend is ok/i, { timeout: 10_000 })

  // The sidebar's app name comes from the backend's runtime-configurable
  // app_name (see backend/app/core/config.py), not a hardcoded product name
  // — so it must match the same name reported in the health status line.
  const appName = await page.getByTestId('app-name').textContent()
  await expect(status).toContainText(appName ?? '')
})

test('dashboard shows the greeting and widget grid', async ({ page }) => {
  await page.goto('/')

  // The greeting is the page's h1 and mentions the same configured app name
  // as the sidebar — never a hardcoded assistant name.
  const appName = await page.getByTestId('app-name').textContent()
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(page.getByText(`${appName} is ready to help.`)).toBeVisible()

  await expect(page.getByRole('heading', { name: 'Clock' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Weather' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Reminders' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'To-do' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Shopping list' })).toBeVisible()
})

test('settings page updates the assistant name and it persists on reload', async ({ page }) => {
  await page.goto('/settings')

  const nameInput = page.getByLabel('Assistant name')
  const originalName = await nameInput.inputValue()

  await nameInput.fill('E2E Test Assistant')
  await page.getByRole('button', { name: 'Save' }).click()
  await expect(page.getByText('Saved.')).toBeVisible()

  await page.reload()
  await expect(page.getByLabel('Assistant name')).toHaveValue('E2E Test Assistant')

  // Restore the original value — the backend this test drives against is a
  // real dev database (not sandboxed like the unit/integration suites), so
  // leaving the rename in place would make this test non-idempotent and
  // pollute the app name for anyone running the app locally afterward.
  await page.getByLabel('Assistant name').fill(originalName)
  await page.getByRole('button', { name: 'Save' }).click()
  await expect(page.getByText('Saved.')).toBeVisible()
})

test('onboarding walks a first-run user through naming the assistant and choosing a theme', async ({
  page,
  request,
}) => {
  const before = await request.get(`${BACKEND_URL}/api/v1/settings`)
  const original = (await before.json()) as { app_name: string; default_theme: string }

  await request.patch(`${BACKEND_URL}/api/v1/settings`, {
    data: { onboarding_complete: false },
  })

  try {
    // A fresh visit to any route redirects to /onboarding while incomplete.
    await page.goto('/')
    await expect(page).toHaveURL(/\/onboarding$/)
    await expect(page.getByRole('heading', { level: 1, name: 'Welcome' })).toBeVisible()

    // Prefilled from the real current settings, never a hardcoded default.
    const nameInput = page.getByLabel('What should we call your assistant?')
    await expect(nameInput).toHaveValue(original.app_name)

    await nameInput.fill('E2E Onboarded Assistant')
    await page.getByLabel('Theme').selectOption('dark')
    await page.getByRole('button', { name: 'Get started' }).click()

    // Completing onboarding lands on the dashboard, and the new name is
    // visible immediately (round-tripped through Settings, not just saved).
    await expect(page).toHaveURL('/')
    await expect(page.getByTestId('app-name')).toHaveText('E2E Onboarded Assistant')

    // Re-runnable, not a one-time irreversible gate: visiting it again
    // (via the Settings page's link) still works after completion.
    await page.goto('/settings')
    await page.getByRole('link', { name: 'Run setup again' }).click()
    await expect(page).toHaveURL(/\/onboarding$/)
    await expect(page.getByLabel('What should we call your assistant?')).toHaveValue(
      'E2E Onboarded Assistant',
    )
  } finally {
    // Restore original state — this test drives the real dev database, not
    // a sandboxed one, same reasoning as the settings rename test below.
    await request.patch(`${BACKEND_URL}/api/v1/settings`, {
      data: {
        app_name: original.app_name,
        default_theme: original.default_theme,
        onboarding_complete: true,
      },
    })
  }
})

test('theme toggle switches between light and dark mode', async ({ page }) => {
  await page.goto('/')

  const toggle = page.getByRole('button', { name: /switch to (dark|light) mode/i })
  const classBefore = await page.locator('html').getAttribute('class')

  await toggle.click()

  await expect(page.locator('html')).not.toHaveAttribute('class', classBefore ?? '')
})

test('shows the 404 page for an unknown route', async ({ page }) => {
  await page.goto('/does-not-exist')

  await expect(page.getByRole('heading', { name: 'Page not found' })).toBeVisible()
  await page.getByRole('link', { name: 'Back to Home' }).click()
  await expect(page).toHaveURL('/')
})

test('mobile drawer nav opens and closes', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 })
  await page.goto('/')

  await page.getByRole('button', { name: 'Open navigation' }).click()
  await expect(page.getByRole('button', { name: 'Close navigation' })).toBeVisible()

  await page.getByRole('button', { name: 'Close navigation' }).click()
  await expect(page.getByRole('button', { name: 'Close navigation' })).not.toBeVisible()
})
