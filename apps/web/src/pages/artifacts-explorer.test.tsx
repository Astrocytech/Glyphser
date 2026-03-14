import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderApp } from '@/test/test-utils'

describe('ArtifactsExplorerPage', () => {
  test('filters files and previews selected artifact', async () => {
    const user = userEvent.setup()
    renderApp('/artifacts/run_mock_004')

    expect(await screen.findByText(/request\.json/i)).toBeInTheDocument()

    await user.type(screen.getByPlaceholderText(/filter/i), 'zzz')
    expect(await screen.findByText(/no files/i)).toBeInTheDocument()

    await user.clear(screen.getByPlaceholderText(/filter/i))
    await user.click(await screen.findByText(/request\.json/i))

    expect(
      await screen.findByText('\"path\": \"/tmp/artifact.bin\"'),
    ).toBeInTheDocument()
  })
})
