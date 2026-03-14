import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderApp } from '@/test/test-utils'

describe('VerifyPage', () => {
  test('validates that at least one input is provided', async () => {
    const user = userEvent.setup()
    renderApp('/verify')

    await user.click(
      screen.getByRole('button', { name: /run verification/i }),
    )

    expect(
      await screen.findByText(/provide at least an artifact path/i),
    ).toBeInTheDocument()
  })

  test('submits and shows result in mock mode', async () => {
    const user = userEvent.setup()
    renderApp('/verify')

    await user.type(
      screen.getByPlaceholderText(/artifact path or run id/i),
      '/tmp/example.bin',
    )
    await user.click(
      screen.getByRole('button', { name: /run verification/i }),
    )

    expect(await screen.findByText('PASS')).toBeInTheDocument()
    expect(await screen.findByText(/run id:/i)).toBeInTheDocument()
  })
})

