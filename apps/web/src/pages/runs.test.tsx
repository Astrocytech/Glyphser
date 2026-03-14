import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderApp } from '@/test/test-utils'

describe('RunsPage', () => {
  test('renders runs and navigates to run details', async () => {
    const user = userEvent.setup()
    renderApp('/runs')

    const runLink = await screen.findByText(/run_mock_004/i)
    expect(runLink).toBeInTheDocument()

    await user.click(runLink)

    expect(await screen.findByText(/details for a single verification run/i)).toBeInTheDocument()
    expect(await screen.findByText(/run_mock_004/i)).toBeInTheDocument()
  })
})

