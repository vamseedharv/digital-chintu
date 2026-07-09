import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Text } from '../../components/ui/Text'

describe('Text', () => {
  it('renders as a paragraph with the body variant by default', () => {
    render(<Text>Hello</Text>)
    const el = screen.getByText('Hello')
    expect(el.tagName).toBe('P')
    expect(el).toHaveClass('text-slate-700')
  })

  it('applies the muted variant', () => {
    render(<Text variant="muted">Hello</Text>)
    expect(screen.getByText('Hello')).toHaveClass('text-slate-500')
  })
})
