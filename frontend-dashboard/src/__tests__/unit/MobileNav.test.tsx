import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { MobileNav } from '../../components/layout/MobileNav'

describe('MobileNav', () => {
  it('renders nothing when closed', () => {
    render(
      <MemoryRouter>
        <MobileNav appName="Chintu" open={false} onClose={() => {}} />
      </MemoryRouter>,
    )

    expect(screen.queryByRole('navigation', { name: 'Primary' })).not.toBeInTheDocument()
  })

  it('renders the nav and moves focus to the close button when open', () => {
    render(
      <MemoryRouter>
        <MobileNav appName="Chintu" open onClose={() => {}} />
      </MemoryRouter>,
    )

    expect(screen.getByRole('navigation', { name: 'Primary' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Close navigation' })).toHaveFocus()
  })

  it('calls onClose when Escape is pressed', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(
      <MemoryRouter>
        <MobileNav appName="Chintu" open onClose={onClose} />
      </MemoryRouter>,
    )

    await user.keyboard('{Escape}')
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onClose when a nav link is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(
      <MemoryRouter>
        <MobileNav appName="Chintu" open onClose={onClose} />
      </MemoryRouter>,
    )

    await user.click(screen.getByRole('link', { name: /home/i }))
    expect(onClose).toHaveBeenCalled()
  })

  it('does not close on a key other than Escape', async () => {
    // 'a' specifically — unlike Enter/Space, it has no native activation
    // behavior on the focused close button, so this isolates the
    // Escape-only check in the keydown listener from browser button semantics.
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(
      <MemoryRouter>
        <MobileNav appName="Chintu" open onClose={onClose} />
      </MemoryRouter>,
    )

    await user.keyboard('a')
    expect(onClose).not.toHaveBeenCalled()
  })

  it('styles the current route differently from an inactive one', () => {
    render(
      <MemoryRouter initialEntries={['/somewhere-else']}>
        <MobileNav appName="Chintu" open onClose={() => {}} />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: /home/i })).toHaveClass('text-slate-700')
  })

  it('traps Tab focus: tabbing past the last focusable element wraps to the first', async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <MobileNav appName="Chintu" open onClose={() => {}} />
      </MemoryRouter>,
    )

    // Focusable elements: the close button (focused on open), then the
    // Home and Settings nav links. Tabbing through all of them should wrap
    // back to the close button instead of leaving the drawer.
    await user.tab()
    expect(screen.getByRole('link', { name: /home/i })).toHaveFocus()

    await user.tab()
    expect(screen.getByRole('link', { name: /settings/i })).toHaveFocus()

    await user.tab()
    expect(screen.getByRole('button', { name: 'Close navigation' })).toHaveFocus()
  })

  it('traps Shift+Tab focus: tabbing back from the first element wraps to the last', async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <MobileNav appName="Chintu" open onClose={() => {}} />
      </MemoryRouter>,
    )

    // Starts on the close button (focused on open); Shift+Tab should wrap
    // to the last focusable element (Settings) instead of leaving the drawer.
    await user.tab({ shift: true })
    expect(screen.getByRole('link', { name: /settings/i })).toHaveFocus()
  })
})
