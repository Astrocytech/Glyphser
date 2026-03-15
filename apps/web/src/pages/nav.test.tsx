import { screen } from '@testing-library/react'
import { renderApp } from '@/test/test-utils'

describe('Navigation', () => {
  test('renders sidebar with all nav items', async () => {
    renderApp('/')

    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
    expect(await screen.findByText('Verify')).toBeInTheDocument()
    expect(await screen.findByText('Runs')).toBeInTheDocument()
    expect(await screen.findByText('Artifacts')).toBeInTheDocument()
    expect(await screen.findByText('Jobs API')).toBeInTheDocument()
    expect(await screen.findByText('Doctor')).toBeInTheDocument()
    expect(await screen.findByText('Setup')).toBeInTheDocument()
    expect(await screen.findByText('Route Run')).toBeInTheDocument()
    expect(await screen.findByText('Certify')).toBeInTheDocument()
    expect(await screen.findByText('Conformance')).toBeInTheDocument()
    expect(await screen.findByText('API Tools')).toBeInTheDocument()
    expect(await screen.findByText('Explorer')).toBeInTheDocument()
    expect(await screen.findByText('Docs')).toBeInTheDocument()
    expect(await screen.findByText('Settings')).toBeInTheDocument()
  })

  test('shows page title in header', async () => {
    renderApp('/')

    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
    expect(await screen.findByText('KPIs, stats, and recent verification runs')).toBeInTheDocument()
  })

  test('shows correct title for verify page', async () => {
    renderApp('/verify')

    expect(await screen.findByText('Submit artifacts or manifests for verification')).toBeInTheDocument()
  })

  test('shows correct title for settings page', async () => {
    renderApp('/settings')

    expect(await screen.findByText('API endpoints, theme, and refresh settings')).toBeInTheDocument()
  })
})
