import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ClockWidget } from '../../components/dashboard/ClockWidget'

function formattedTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function formattedDate(date: Date): string {
  return date.toLocaleDateString([], {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

describe('ClockWidget', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2024, 0, 1, 9, 5, 0))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders the current time and date', () => {
    render(<ClockWidget />)

    expect(screen.getByRole('heading', { level: 2, name: 'Clock' })).toBeInTheDocument()
    expect(screen.getByText(formattedTime(new Date(2024, 0, 1, 9, 5, 0)))).toBeInTheDocument()
    expect(screen.getByText(formattedDate(new Date(2024, 0, 1, 9, 5, 0)))).toBeInTheDocument()
  })

  it('ticks forward as time passes', () => {
    render(<ClockWidget />)

    // beforeEach fixes the clock at 09:05:00; advancing by a minute of fake
    // time should move the displayed time forward by exactly that much.
    act(() => {
      vi.advanceTimersByTime(60_000)
    })

    expect(screen.getByText(formattedTime(new Date(2024, 0, 1, 9, 6, 0)))).toBeInTheDocument()
  })

  it('stops ticking after unmount (no timer leak)', () => {
    const { unmount } = render(<ClockWidget />)
    unmount()

    // If the interval weren't cleared, this would throw a React
    // act()/state-update-on-unmounted-component warning that Vitest surfaces
    // as a failure via console.error.
    expect(() => {
      act(() => {
        vi.advanceTimersByTime(5_000)
      })
    }).not.toThrow()
  })
})
