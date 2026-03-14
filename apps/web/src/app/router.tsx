import { createBrowserRouter } from 'react-router-dom'
import AppLayout from './layout'
import DashboardPage from '@/pages/dashboard'
import VerifyPage from '@/pages/verify'
import RunsPage from '@/pages/runs'
import RunDetailsPage from '@/pages/run-details'
import ArtifactsPage from '@/pages/artifacts'
import ArtifactsExplorerPage from '@/pages/artifacts-explorer'
import SettingsPage from '@/pages/settings'

export const router = createBrowserRouter([
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
])
