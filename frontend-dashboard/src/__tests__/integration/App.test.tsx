import { render, screen, waitFor } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { routes } from '../../app/router'
import { ThemeProvider } from '../../theme/ThemeProvider'

function renderApp(initialEntries: string[] = ['/']) {
  const router = createMemoryRouter(routes, { initialEntries })
  return render(
    <ThemeProvider>
      <RouterProvider router={router} />
    </ThemeProvider>,
  )
}

describe('App', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'ok', app_name: 'Chintu', environment: 'test' }),
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders the app name in the sidebar', () => {
    renderApp()
    expect(screen.getByText('Digital Chintu')).toBeInTheDocument()
  })

  it('shows the backend health status once loaded', async () => {
    renderApp()

    expect(screen.getByRole('status')).toHaveTextContent(/checking backend health/i)

    await waitFor(() => {
      expect(screen.getByText(/Chintu backend is ok/)).toBeInTheDocument()
    })
  })

  it('renders the dashboard widgets, greeting the configured app name', async () => {
    renderApp()

    await waitFor(() => {
      expect(screen.getByText('Chintu is ready to help.')).toBeInTheDocument()
    })
    expect(screen.getByRole('heading', { level: 2, name: 'Clock' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Weather' })).toBeInTheDocument()
  })

  it('shows an error state when the backend is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))

    renderApp()

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Could not reach the backend')
    })
  })

  it('toggles between light and dark mode', async () => {
    const { user } = await import('@testing-library/user-event').then((m) => ({
      user: m.default.setup(),
    }))

    renderApp()

    const toggle = screen.getByRole('button', { name: /switch to (dark|light) mode/i })
    const initialLabel = toggle.textContent

    await user.click(toggle)

    expect(toggle.textContent).not.toBe(initialLabel)
  })

  it('shows the 404 page for an unknown route', () => {
    renderApp(['/does-not-exist'])

    expect(screen.getByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
  })

  it('opens the mobile nav when the hamburger button is clicked', async () => {
    const { user } = await import('@testing-library/user-event').then((m) => ({
      user: m.default.setup(),
    }))

    renderApp()

    // The mobile nav only renders (at all, in the DOM) while open — its
    // "Close navigation" button is a reliable marker for that, since the
    // always-present desktop Sidebar shares the same "Primary" nav label
    // (they're mutually exclusive only via CSS, which jsdom doesn't apply).
    expect(screen.queryByRole('button', { name: 'Close navigation' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Open navigation' }))

    expect(screen.getByRole('button', { name: 'Close navigation' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Close navigation' }))

    // AnimatePresence keeps the element mounted for its exit transition.
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: 'Close navigation' })).not.toBeInTheDocument()
    })
  })
})
