import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Compass } from 'lucide-react'
import { EmptyState } from '../../components/ui/EmptyState'

describe('EmptyState', () => {
  it('renders the icon, title, description, and action', () => {
    render(
      <EmptyState
        icon={Compass}
        title="Nothing here"
        description="Nothing to show yet."
        action={<button>Do something</button>}
      />,
    )

    expect(screen.getByRole('heading', { name: 'Nothing here' })).toBeInTheDocument()
    expect(screen.getByText('Nothing to show yet.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Do something' })).toBeInTheDocument()
  })

  it('renders without a description or action', () => {
    render(<EmptyState icon={Compass} title="Nothing here" />)
    expect(screen.getByRole('heading', { name: 'Nothing here' })).toBeInTheDocument()
  })
})
