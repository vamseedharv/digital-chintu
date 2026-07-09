import { createBrowserRouter } from 'react-router'
import type { RouteObject } from 'react-router'
import { AppShell } from './AppShell'
import { HomePage } from '../routes/HomePage'
import { NotFoundPage } from '../routes/NotFoundPage'
import { ErrorPage } from '../routes/ErrorPage'

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppShell />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]

export const router = createBrowserRouter(routes)
