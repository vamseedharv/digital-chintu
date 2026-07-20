import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { OnboardingPage } from '../../routes/OnboardingPage'

function renderPage() {
  const router = createMemoryRouter(
    [
      { path: '/onboarding', element: <OnboardingPage /> },
      { path: '/', element: <div>Landed on dashboard</div> },
    ],
    { initialEntries: ['/onboarding'] },
  )
  return render(<RouterProvider router={router} />)
}

describe('OnboardingPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          app_name: 'Chintu',
          default_theme: 'system',
          onboarding_complete: false,
        }),
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shows a loading state before current settings arrive', () => {
    renderPage()

    expect(screen.getByRole('status')).toHaveTextContent(/loading current settings/i)
  })

  it('prefills the form with the current settings, never a hardcoded default', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('What should we call your assistant?')).toHaveValue('Chintu')
    })
    expect(screen.getByLabelText('Theme')).toHaveValue('system')
  })

  it('shows an error state when current settings fail to load', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Could not load current settings')
    })
  })

  it('saves the entered name/theme, marks onboarding complete, and lands on the dashboard', async () => {
    const user = userEvent.setup()
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          app_name: 'Chintu',
          default_theme: 'system',
          onboarding_complete: false,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          app_name: 'Jarvis',
          default_theme: 'dark',
          onboarding_complete: true,
        }),
      })
    vi.stubGlobal('fetch', fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('What should we call your assistant?')).toHaveValue('Chintu')
    })

    const input = screen.getByLabelText('What should we call your assistant?')
    await user.clear(input)
    await user.type(input, 'Jarvis')
    await user.selectOptions(screen.getByLabelText('Theme'), 'dark')
    await user.click(screen.getByRole('button', { name: 'Get started' }))

    await waitFor(() => {
      expect(screen.getByText('Landed on dashboard')).toBeInTheDocument()
    })

    expect(fetchMock.mock.calls[1]?.[1]).toMatchObject({
      method: 'PATCH',
      body: JSON.stringify({
        app_name: 'Jarvis',
        default_theme: 'dark',
        onboarding_complete: true,
      }),
    })
  })

  it('skip marks onboarding complete without changing name/theme, and lands on the dashboard', async () => {
    const user = userEvent.setup()
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          app_name: 'Chintu',
          default_theme: 'system',
          onboarding_complete: false,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          app_name: 'Chintu',
          default_theme: 'system',
          onboarding_complete: true,
        }),
      })
    vi.stubGlobal('fetch', fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('What should we call your assistant?')).toHaveValue('Chintu')
    })

    await user.click(screen.getByRole('button', { name: 'Skip for now' }))

    await waitFor(() => {
      expect(screen.getByText('Landed on dashboard')).toBeInTheDocument()
    })

    expect(fetchMock.mock.calls[1]?.[1]).toMatchObject({
      method: 'PATCH',
      body: JSON.stringify({ onboarding_complete: true }),
    })
  })

  it('shows an error message when saving fails, without navigating away', async () => {
    const user = userEvent.setup()
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          app_name: 'Chintu',
          default_theme: 'system',
          onboarding_complete: false,
        }),
      })
      .mockRejectedValueOnce(new Error('network error'))
    vi.stubGlobal('fetch', fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('What should we call your assistant?')).toHaveValue('Chintu')
    })

    await user.click(screen.getByRole('button', { name: 'Get started' }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Could not save your settings')
    })
    expect(screen.queryByText('Landed on dashboard')).not.toBeInTheDocument()
  })
})
