import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { GreetingWidget } from '../../components/dashboard/GreetingWidget'

describe('GreetingWidget', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('greets with a time-of-day message as the page heading', () => {
    vi.setSystemTime(new Date(2024, 0, 1, 9, 0, 0))

    render(<GreetingWidget appName="Chintu" />)

    expect(screen.getByRole('heading', { level: 1, name: 'Good morning' })).toBeInTheDocument()
  })

  it('mentions the configured assistant name, never a hardcoded one', () => {
    vi.setSystemTime(new Date(2024, 0, 1, 9, 0, 0))

    render(<GreetingWidget appName="Jarvis" />)

    expect(screen.getByText('Jarvis is ready to help.')).toBeInTheDocument()
  })

  it('updates the greeting when the time-of-day bucket changes while mounted', () => {
    vi.setSystemTime(new Date(2024, 0, 1, 11, 59, 0))

    render(<GreetingWidget appName="Chintu" />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Good morning')

    vi.setSystemTime(new Date(2024, 0, 1, 12, 1, 0))
    act(() => {
      vi.advanceTimersByTime(60_000)
    })

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Good afternoon')
  })
})
