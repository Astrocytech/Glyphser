import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { render } from '@testing-library/react'
import AppLayout from '@/app/layout'
import DashboardPage from '@/pages/dashboard'
import VerifyPage from '@/pages/verify'
import RunsPage from '@/pages/runs'
import RunDetailsPage from '@/pages/run-details'
import ArtifactsPage from '@/pages/artifacts'
import ArtifactsExplorerPage from '@/pages/artifacts-explorer'
import SettingsPage from '@/pages/settings'

export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}

export function renderApp(initialPath = '/') {
  const queryClient = createTestQueryClient()

  const router = createMemoryRouter(
    [
      {
        path: '/',
        element: <AppLayout />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: 'verify', element: <VerifyPage /> },
          { path: 'runs', element: <RunsPage /> },
          { path: 'runs/:runId', element: <RunDetailsPage /> },
          { path: 'artifacts', element: <ArtifactsPage /> },
          { path: 'artifacts/:runId', element: <ArtifactsExplorerPage /> },
          { path: 'settings', element: <SettingsPage /> },
        ],
      },
    ],
    { initialEntries: [initialPath] },
  )

  const utils = render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )

  return { ...utils, queryClient, router }
}

