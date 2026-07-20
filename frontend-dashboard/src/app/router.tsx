import { createBrowserRouter } from 'react-router'
import type { RouteObject } from 'react-router'
import { AppShell } from './AppShell'
import { DashboardPage } from '../routes/DashboardPage'
import { SettingsPage } from '../routes/SettingsPage'
import { NotFoundPage } from '../routes/NotFoundPage'
import { ErrorPage } from '../routes/ErrorPage'

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppShell />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]

export const router = createBrowserRouter(routes)
