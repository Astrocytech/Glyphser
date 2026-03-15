import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import { ErrorBoundary } from '@/components/state/error-boundary'
import AppLayout from './layout'
import LoadingState from '@/components/state/loading-state'

const DashboardPage = lazy(() => import('@/pages/dashboard'))
const VerifyPage = lazy(() => import('@/pages/verify'))
const RunsPage = lazy(() => import('@/pages/runs'))
const RunDetailsPage = lazy(() => import('@/pages/run-details'))
const ArtifactsPage = lazy(() => import('@/pages/artifacts'))
const ArtifactsExplorerPage = lazy(() => import('@/pages/artifacts-explorer'))
const JobsApiPage = lazy(() => import('@/pages/jobs-api'))
const DoctorPage = lazy(() => import('@/pages/doctor'))
const SetupPage = lazy(() => import('@/pages/setup'))
const RouteRunPage = lazy(() => import('@/pages/route-run'))
const CertifyPage = lazy(() => import('@/pages/certify'))
const ConformancePage = lazy(() => import('@/pages/conformance'))
const ApiToolsPage = lazy(() => import('@/pages/api-tools'))
const ModuleExplorerPage = lazy(() => import('@/pages/module-explorer'))
const DocsPage = lazy(() => import('@/pages/docs'))
const SettingsPage = lazy(() => import('@/pages/settings'))

function PageLoader() {
  return <LoadingState label="Loading page..." />
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<PageLoader />}>
            <DashboardPage />
          </Suspense>
        ),
      },
      {
        path: 'verify',
        element: (
          <Suspense fallback={<PageLoader />}>
            <VerifyPage />
          </Suspense>
        ),
      },
      {
        path: 'runs',
        element: (
          <Suspense fallback={<PageLoader />}>
            <RunsPage />
          </Suspense>
        ),
      },
      {
        path: 'runs/:runId',
        element: (
          <Suspense fallback={<PageLoader />}>
            <RunDetailsPage />
          </Suspense>
        ),
      },
      {
        path: 'artifacts',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ArtifactsPage />
          </Suspense>
        ),
      },
      {
        path: 'artifacts/:runId',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ArtifactsExplorerPage />
          </Suspense>
        ),
      },
      {
        path: 'jobs-api',
        element: (
          <Suspense fallback={<PageLoader />}>
            <JobsApiPage />
          </Suspense>
        ),
      },
      {
        path: 'doctor',
        element: (
          <Suspense fallback={<PageLoader />}>
            <DoctorPage />
          </Suspense>
        ),
      },
      {
        path: 'setup',
        element: (
          <Suspense fallback={<PageLoader />}>
            <SetupPage />
          </Suspense>
        ),
      },
      {
        path: 'route-run',
        element: (
          <Suspense fallback={<PageLoader />}>
            <RouteRunPage />
          </Suspense>
        ),
      },
      {
        path: 'certify',
        element: (
          <Suspense fallback={<PageLoader />}>
            <CertifyPage />
          </Suspense>
        ),
      },
      {
        path: 'conformance',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ConformancePage />
          </Suspense>
        ),
      },
      {
        path: 'api-tools',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ApiToolsPage />
          </Suspense>
        ),
      },
      {
        path: 'module-explorer',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ModuleExplorerPage />
          </Suspense>
        ),
      },
      {
        path: 'docs',
        element: (
          <Suspense fallback={<PageLoader />}>
            <DocsPage />
          </Suspense>
        ),
      },
      {
        path: 'settings',
        element: (
          <Suspense fallback={<PageLoader />}>
            <SettingsPage />
          </Suspense>
        ),
      },
    ],
  },
])