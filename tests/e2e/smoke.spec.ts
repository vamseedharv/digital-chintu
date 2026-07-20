import { expect, test } from '@playwright/test'

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
