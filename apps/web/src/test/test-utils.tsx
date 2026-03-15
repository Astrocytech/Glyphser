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
import JobsApiPage from '@/pages/jobs-api'
import DoctorPage from '@/pages/doctor'
import SetupPage from '@/pages/setup'
import RouteRunPage from '@/pages/route-run'
import CertifyPage from '@/pages/certify'
import ConformancePage from '@/pages/conformance'
import ApiToolsPage from '@/pages/api-tools'
import ModuleExplorerPage from '@/pages/module-explorer'
import DocsPage from '@/pages/docs'
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
          { path: 'jobs-api', element: <JobsApiPage /> },
          { path: 'doctor', element: <DoctorPage /> },
          { path: 'setup', element: <SetupPage /> },
          { path: 'route-run', element: <RouteRunPage /> },
          { path: 'certify', element: <CertifyPage /> },
          { path: 'conformance', element: <ConformancePage /> },
          { path: 'api-tools', element: <ApiToolsPage /> },
          { path: 'module-explorer', element: <ModuleExplorerPage /> },
          { path: 'docs', element: <DocsPage /> },
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
