import { render, screen } from '@testing-library/react'
import { createMemoryRouter, Outlet, RouterProvider } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { DashboardPage } from '../../routes/DashboardPage'
import type { AppShellContext } from '../../app/AppShell'

function ParentWithContext({ appName = 'Chintu' }: { appName?: string }) {
  const health: AppShellContext['health'] = {
    kind: 'success',
    data: { status: 'ok', app_name: appName, environment: 'test' },
  }
  return <Outlet context={{ health, appName } satisfies AppShellContext} />
}

function renderDashboard(appName?: string) {
  const router = createMemoryRouter([
    {
      path: '/',
      element: <ParentWithContext appName={appName} />,
      children: [{ index: true, element: <DashboardPage /> }],
    },
  ])

  return render(<RouterProvider router={router} />)
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2024, 0, 1, 9, 0, 0))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('greets using the configured assistant name, not a hardcoded one', () => {
    renderDashboard('Jarvis')

    expect(screen.getByRole('heading', { level: 1, name: 'Good morning' })).toBeInTheDocument()
    expect(screen.getByText('Jarvis is ready to help.')).toBeInTheDocument()
  })

  it('renders the clock, system status, and placeholder widgets', () => {
    renderDashboard()

    expect(screen.getByRole('heading', { level: 2, name: 'Clock' })).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { level: 2, name: 'Backend connection' }),
    ).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Weather' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Reminders' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'To-do' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Shopping list' })).toBeInTheDocument()
  })

  it('still shows the real backend health status alongside the widgets', () => {
    renderDashboard('Chintu')

    expect(screen.getByText(/Chintu backend is ok/)).toBeInTheDocument()
  })
})
