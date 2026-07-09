import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Skeleton } from '../../components/ui/Skeleton'

describe('Skeleton', () => {
  it('renders as a purely decorative, aria-hidden placeholder', () => {
    const { container } = render(<Skeleton className="h-4 w-48" data-testid="skeleton" />)
    const skeleton = container.querySelector('[data-testid="skeleton"]')

    expect(skeleton).toHaveAttribute('aria-hidden', 'true')
    expect(skeleton).toHaveClass('animate-pulse', 'h-4', 'w-48')
  })
})
