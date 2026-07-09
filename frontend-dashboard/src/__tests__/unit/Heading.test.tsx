import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Heading } from '../../components/ui/Heading'

describe('Heading', () => {
  it('defaults to an h1', () => {
    render(<Heading>Title</Heading>)
    expect(screen.getByRole('heading', { level: 1, name: 'Title' })).toBeInTheDocument()
  })

  it('renders the requested heading level', () => {
    render(<Heading level={3}>Subsection</Heading>)
    expect(screen.getByRole('heading', { level: 3, name: 'Subsection' })).toBeInTheDocument()
  })
})
