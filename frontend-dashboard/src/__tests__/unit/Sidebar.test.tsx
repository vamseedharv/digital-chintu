import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import { Sidebar } from '../../components/layout/Sidebar'

describe('Sidebar', () => {
  it('renders the app name and nav links', () => {
    render(
      <MemoryRouter>
        <Sidebar appName="Chintu" />
      </MemoryRouter>,
    )

    expect(screen.getByText('Chintu')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /home/i })).toHaveAttribute('href', '/')
  })

  it('is a labeled navigation landmark', () => {
    render(
      <MemoryRouter>
        <Sidebar appName="Chintu" />
      </MemoryRouter>,
    )

    expect(screen.getByRole('navigation', { name: 'Primary' })).toBeInTheDocument()
  })
})
