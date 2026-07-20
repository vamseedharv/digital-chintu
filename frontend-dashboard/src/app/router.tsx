import { createBrowserRouter } from 'react-router'
import type { RouteObject } from 'react-router'
import { AppShell } from './AppShell'
import { DashboardPage } from '../routes/DashboardPage'
import { OnboardingPage } from '../routes/OnboardingPage'
import { SettingsPage } from '../routes/SettingsPage'
import { NotFoundPage } from '../routes/NotFoundPage'
import { ErrorPage } from '../routes/ErrorPage'

export const routes: RouteObject[] = [
  // A sibling of AppShell, not a child of it: onboarding is a focused,
  // full-screen flow without sidebar/nav chrome. See AppShell.tsx for the
  // redirect-gate that sends incomplete-onboarding users here.
  { path: '/onboarding', element: <OnboardingPage />, errorElement: <ErrorPage /> },
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
