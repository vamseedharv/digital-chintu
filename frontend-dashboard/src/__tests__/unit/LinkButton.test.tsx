import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import { LinkButton } from '../../components/ui/LinkButton'

describe('LinkButton', () => {
  it('renders a real link, not a button, styled like the primary Button', () => {
    render(
      <MemoryRouter>
        <LinkButton to="/">Back to Home</LinkButton>
      </MemoryRouter>,
    )

    const link = screen.getByRole('link', { name: 'Back to Home' })
    expect(link).toHaveAttribute('href', '/')
    expect(link).toHaveClass('bg-brand-600')
  })

  it('applies the requested variant', () => {
    render(
      <MemoryRouter>
        <LinkButton to="/" variant="secondary">
          Cancel
        </LinkButton>
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: 'Cancel' })).toHaveClass('border-slate-300')
  })
})
