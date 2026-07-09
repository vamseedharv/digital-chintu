import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../../App'
import { ThemeProvider } from '../../theme/ThemeProvider'

function renderApp() {
  return render(
    <ThemeProvider>
      <App />
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

  it('renders the app title', () => {
    renderApp()
    expect(screen.getByRole('heading', { name: 'Digital Chintu' })).toBeInTheDocument()
  })

  it('shows the backend health status once loaded', async () => {
    renderApp()

    expect(screen.getByRole('status')).toHaveTextContent('Checking backend health')

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent(/Chintu backend is ok/)
    })
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
})
