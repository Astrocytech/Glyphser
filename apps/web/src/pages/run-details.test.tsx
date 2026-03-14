import { screen } from '@testing-library/react'
import { renderApp } from '@/test/test-utils'

describe('RunDetailsPage', () => {
  test('shows an error for a missing run', async () => {
    renderApp('/runs/run_does_not_exist')

    expect(await screen.findByText(/run not found/i)).toBeInTheDocument()
  })
})

