import { act, render, renderHook, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ThemeProvider } from '../../theme/ThemeProvider'
import { useTheme } from '../../theme/useTheme'

const STORAGE_KEY = 'chintu-theme'

function mockMatchMedia(matches: boolean) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })) as unknown as typeof window.matchMedia
}

describe('ThemeProvider / useTheme', () => {
  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  afterEach(() => {
    window.localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('throws when useTheme is called outside a ThemeProvider', () => {
    // Prevent React from logging the expected error to the test output.
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

    expect(() => renderHook(() => useTheme())).toThrow(
      'useTheme must be used within a ThemeProvider',
    )

    consoleError.mockRestore()
  })

  it('defaults to the OS color-scheme preference when nothing is stored', () => {
    mockMatchMedia(true) // prefers-color-scheme: dark

    const { result } = renderHook(() => useTheme(), { wrapper: ThemeProvider })

    expect(result.current.theme).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('prefers a previously stored theme over the OS preference', () => {
    mockMatchMedia(true) // OS prefers dark...
    window.localStorage.setItem(STORAGE_KEY, 'light') // ...but the user chose light before.

    const { result } = renderHook(() => useTheme(), { wrapper: ThemeProvider })

    expect(result.current.theme).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggleTheme flips the theme, updates the <html> class, and persists to localStorage', () => {
    mockMatchMedia(false)

    const { result } = renderHook(() => useTheme(), { wrapper: ThemeProvider })

    expect(result.current.theme).toBe('light')

    act(() => {
      result.current.toggleTheme()
    })

    expect(result.current.theme).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe('dark')

    act(() => {
      result.current.toggleTheme()
    })

    expect(result.current.theme).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe('light')
  })

  it('renders children', async () => {
    mockMatchMedia(false)
    const user = userEvent.setup()

    render(
      <ThemeProvider>
        <button onClick={() => {}}>hello</button>
      </ThemeProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'hello' }))
    expect(screen.getByText('hello')).toBeInTheDocument()
  })
})
