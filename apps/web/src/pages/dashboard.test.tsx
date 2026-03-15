import { screen } from '@testing-library/react'
import { renderApp } from '@/test/test-utils'

describe('DashboardPage', () => {
  test('renders dashboard with stats cards', async () => {
    renderApp('/')

    expect(await screen.findByText('Total Runs')).toBeInTheDocument()
    expect(await screen.findByText('Passed')).toBeInTheDocument()
    expect(await screen.findByText('Failed')).toBeInTheDocument()
    expect(await screen.findByText('Running')).toBeInTheDocument()
  })

  test('renders recent runs section', async () => {
    renderApp('/')

    expect(await screen.findByText('Recent Runs')).toBeInTheDocument()
  })

  test('shows link to runs page', async () => {
    renderApp('/')

    const viewAllLink = await screen.findByText(/view all/i)
    expect(viewAllLink).toBeInTheDocument()
  })
})
