import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { SettingsPage } from '../../routes/SettingsPage'

function renderPage() {
  return render(
    <MemoryRouter>
      <SettingsPage />
    </MemoryRouter>,
  )
}

describe('SettingsPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          app_name: 'Chintu',
          default_theme: 'system',
          onboarding_complete: true,
        }),
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shows a loading state before settings arrive', () => {
    renderPage()

    expect(screen.getByRole('status')).toHaveTextContent(/loading settings/i)
  })

  it('populates the form with the fetched settings', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('Assistant name')).toHaveValue('Chintu')
    })
    expect(screen.getByLabelText('Theme')).toHaveValue('system')
  })

  it('shows an error state when settings fail to load', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Could not load settings')
    })
  })

  it('saves an edited assistant name and shows confirmation', async () => {
    const user = userEvent.setup()
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ app_name: 'Chintu', default_theme: 'system' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ app_name: 'Jarvis', default_theme: 'system' }),
      })
    vi.stubGlobal('fetch', fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('Assistant name')).toHaveValue('Chintu')
    })

    const input = screen.getByLabelText('Assistant name')
    await user.clear(input)
    await user.type(input, 'Jarvis')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() => {
      expect(screen.getByText('Saved.')).toBeInTheDocument()
    })

    expect(fetchMock.mock.calls).toHaveLength(2)
    expect(fetchMock.mock.calls[1]?.[1]).toMatchObject({
      method: 'PATCH',
      body: JSON.stringify({ app_name: 'Jarvis', default_theme: 'system' }),
    })
  })

  it('saves an edited theme selection', async () => {
    const user = userEvent.setup()
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ app_name: 'Chintu', default_theme: 'system' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ app_name: 'Chintu', default_theme: 'dark' }),
      })
    vi.stubGlobal('fetch', fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('Theme')).toHaveValue('system')
    })

    await user.selectOptions(screen.getByLabelText('Theme'), 'dark')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() => {
      expect(screen.getByText('Saved.')).toBeInTheDocument()
    })

    expect(fetchMock.mock.calls[1]?.[1]).toMatchObject({
      method: 'PATCH',
      body: JSON.stringify({ app_name: 'Chintu', default_theme: 'dark' }),
    })
  })

  it('links to /onboarding so setup can be re-run', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('Assistant name')).toHaveValue('Chintu')
    })

    expect(screen.getByRole('link', { name: 'Run setup again' })).toHaveAttribute(
      'href',
      '/onboarding',
    )
  })

  it('shows an error message when saving fails, without losing the typed draft', async () => {
    const user = userEvent.setup()
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ app_name: 'Chintu', default_theme: 'system' }),
      })
      .mockRejectedValueOnce(new Error('network error'))
    vi.stubGlobal('fetch', fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('Assistant name')).toHaveValue('Chintu')
    })

    await user.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Could not save settings')
    })
    expect(screen.getByLabelText('Assistant name')).toHaveValue('Chintu')
  })
})
