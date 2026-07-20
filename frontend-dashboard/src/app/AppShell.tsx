import { useEffect, useState } from 'react'
import { Outlet, useNavigate } from 'react-router'
import { Menu } from 'lucide-react'
import { useHealth } from '../api/useHealth'
import type { HealthState } from '../api/useHealth'
import { useSettings } from '../api/useSettings'
import { ThemeToggle } from '../components/ThemeToggle'
import { Sidebar } from '../components/layout/Sidebar'
import { MobileNav } from '../components/layout/MobileNav'
import { PageContainer } from '../components/layout/PageContainer'

const DEFAULT_APP_NAME = 'Digital Chintu'

export interface AppShellContext {
  health: HealthState
  appName: string
}

export function AppShell() {
  const health = useHealth()
  const { state: settingsState } = useSettings()
  const appName = health.kind === 'success' ? health.data.app_name : DEFAULT_APP_NAME
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    document.title = appName
  }, [appName])

  useEffect(() => {
    // AppShell only ever renders for routes other than /onboarding (see
    // router.tsx — onboarding is a sibling route, not a child of this
    // layout), so any incomplete-onboarding user reaching any of them
    // should be sent there. Only acts once the fetch actually resolves —
    // never redirects while loading (avoids a flash) or on a fetch error
    // (can't know onboarding status, so don't guess).
    if (settingsState.kind === 'success' && !settingsState.data.onboarding_complete) {
      navigate('/onboarding', { replace: true })
    }
  }, [settingsState, navigate])

  return (
    <div className="min-h-screen md:flex">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:shadow-lg dark:focus:bg-slate-800"
      >
        Skip to content
      </a>

      <Sidebar appName={appName} />
      <MobileNav appName={appName} open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />

      <div className="flex-1">
        <header className="flex items-center justify-between px-6 py-4 md:justify-end">
          <button
            type="button"
            onClick={() => setMobileNavOpen(true)}
            aria-label="Open navigation"
            className="rounded-lg p-2 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 dark:hover:bg-slate-800 md:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>
          <ThemeToggle />
        </header>

        <PageContainer>
          <main id="main-content">
            <Outlet context={{ health, appName } satisfies AppShellContext} />
          </main>
        </PageContainer>
      </div>
    </div>
  )
}
