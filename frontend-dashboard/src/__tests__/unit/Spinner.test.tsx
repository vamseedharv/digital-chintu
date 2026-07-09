import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Spinner } from '../../components/ui/Spinner'

describe('Spinner', () => {
  it('announces itself to assistive tech via role=status', () => {
    render(<Spinner label="Loading reminders" />)
    expect(screen.getByRole('status', { name: 'Loading reminders' })).toBeInTheDocument()
  })

  it('defaults to a generic loading label', () => {
    render(<Spinner />)
    expect(screen.getByRole('status', { name: 'Loading…' })).toBeInTheDocument()
  })
})
