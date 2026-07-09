import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ThemeToggle } from '../../components/ThemeToggle'
import { ThemeProvider } from '../../theme/ThemeProvider'

describe('ThemeToggle', () => {
  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.classList.remove('dark')
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: false, // start in light mode
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia
  })

  it('labels itself after the mode it will switch to, not the current one', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>,
    )

    // Currently light, so the button offers to switch to dark.
    expect(screen.getByRole('button', { name: 'Switch to dark mode' })).toHaveTextContent(
      'Light mode',
    )
  })

  it('toggles the label and the button name when clicked', async () => {
    const user = userEvent.setup()

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Switch to dark mode' }))

    expect(screen.getByRole('button', { name: 'Switch to light mode' })).toHaveTextContent(
      'Dark mode',
    )
  })

  it('has a visible keyboard focus ring, like every other interactive control', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>,
    )

    expect(screen.getByRole('button')).toHaveClass('focus-visible:ring-2')
  })
})
