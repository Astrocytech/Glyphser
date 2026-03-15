import { createBrowserRouter } from 'react-router-dom'
import { ErrorBoundary } from '@/components/state/error-boundary'
import AppLayout from './layout'
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

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <ErrorBoundary />,
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
])
