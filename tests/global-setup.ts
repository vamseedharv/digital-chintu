/**
 * Runs once before the whole E2E suite. AppShell now redirects to
 * /onboarding whenever `onboarding_complete` is false — the default on a
 * DB that's never had it set. Without this, every test that expects to
 * land on the normal app (dashboard, settings, theme toggle, 404, mobile
 * nav) would instead land on the onboarding wizard. The dedicated
 * onboarding test in e2e/smoke.spec.ts flips this to false and back
 * around its own assertions.
 */
async function globalSetup(): Promise<void> {
  const backendUrl = process.env.PLAYWRIGHT_BACKEND_URL ?? 'http://localhost:8000'

  await fetch(`${backendUrl}/api/v1/settings`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ onboarding_complete: true }),
  })
}

export default globalSetup
