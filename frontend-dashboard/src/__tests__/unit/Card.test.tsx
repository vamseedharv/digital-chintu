import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Card } from '../../components/ui/Card'

describe('Card', () => {
  it('renders its children', () => {
    render(<Card>content</Card>)
    expect(screen.getByText('content')).toBeInTheDocument()
  })

  it('merges a custom className with its default styles', () => {
    render(<Card className="custom-class">content</Card>)
    const card = screen.getByText('content')
    expect(card).toHaveClass('custom-class')
    expect(card).toHaveClass('glass')
  })
})
