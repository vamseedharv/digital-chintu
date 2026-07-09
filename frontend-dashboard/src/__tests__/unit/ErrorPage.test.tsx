import { render, screen, waitFor } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it } from 'vitest'
import { ErrorPage } from '../../routes/ErrorPage'

function ThrowingComponent(): never {
  throw new Error('boom')
}

describe('ErrorPage', () => {
  it('renders a generic message for a thrown JS error', async () => {
    const router = createMemoryRouter(
      [{ path: '/', element: <ThrowingComponent />, errorElement: <ErrorPage /> }],
      { initialEntries: ['/'] },
    )

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Something went wrong' })).toBeInTheDocument()
    })
    expect(screen.getByText(/unexpected error occurred/i)).toBeInTheDocument()
  })

  it('renders the status for a thrown route error response', async () => {
    const router = createMemoryRouter(
      [
        {
          path: '/',
          element: <div />,
          errorElement: <ErrorPage />,
          loader: () => {
            throw new Response('Not Found', { status: 404, statusText: 'Not Found' })
          },
        },
      ],
      { initialEntries: ['/'] },
    )

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText('404 Not Found')).toBeInTheDocument()
    })
  })
})
