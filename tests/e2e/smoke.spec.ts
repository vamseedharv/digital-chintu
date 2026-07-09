import { expect, test } from '@playwright/test'

test('dashboard loads and shows backend health status using the configured app name', async ({
  page,
}) => {
  await page.goto('/')

  const status = page.getByRole('status')
  await expect(status).toContainText(/backend is ok/i, { timeout: 10_000 })

  // The header name comes from the backend's runtime-configurable app_name
  // (see backend/app/core/config.py), not a hardcoded product name — so it
  // must match the same name reported in the health status line.
  const heading = page.getByRole('heading', { level: 1 })
  const headingText = await heading.textContent()
  await expect(status).toContainText(headingText ?? '')
})

test('theme toggle switches between light and dark mode', async ({ page }) => {
  await page.goto('/')

  const toggle = page.getByRole('button', { name: /switch to (dark|light) mode/i })
  const classBefore = await page.locator('html').getAttribute('class')

  await toggle.click()

  await expect(page.locator('html')).not.toHaveAttribute('class', classBefore ?? '')
})
