import { render, screen } from '@testing-library/react'
import { createMemoryRouter, Outlet, RouterProvider } from 'react-router'
import { describe, expect, it } from 'vitest'
import { HomePage } from '../../routes/HomePage'
import type { AppShellContext } from '../../app/AppShell'

function ParentWithContext() {
  const health: AppShellContext['health'] = {
    kind: 'success',
    data: { status: 'ok', app_name: 'Chintu', environment: 'test' },
  }
  return <Outlet context={{ health } satisfies AppShellContext} />
}

describe('HomePage', () => {
  it('renders the health status supplied via outlet context', () => {
    const router = createMemoryRouter([
      {
        path: '/',
        element: <ParentWithContext />,
        children: [{ index: true, element: <HomePage /> }],
      },
    ])

    render(<RouterProvider router={router} />)

    expect(screen.getByRole('heading', { name: 'System status' })).toBeInTheDocument()
    expect(screen.getByText(/Chintu backend is ok/)).toBeInTheDocument()
  })
})
