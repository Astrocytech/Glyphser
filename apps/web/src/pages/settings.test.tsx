import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderApp } from '@/test/test-utils'

describe('SettingsPage', () => {
  test('renders settings page with form fields', async () => {
    renderApp('/settings')

    expect(await screen.findByText('API Configuration')).toBeInTheDocument()
    expect(await screen.findByText('Appearance')).toBeInTheDocument()
    expect(await screen.findByText('Data Refresh')).toBeInTheDocument()
  })

  test('shows API base URL field', async () => {
    renderApp('/settings')

    expect(await screen.findByLabelText(/api base url/i)).toBeInTheDocument()
  })

  test('shows mock API toggle', async () => {
    renderApp('/settings')

    expect(await screen.findByLabelText(/use mock api/i)).toBeInTheDocument()
  })

  test('shows dark mode toggle', async () => {
    renderApp('/settings')

    expect(await screen.findByLabelText(/dark mode/i)).toBeInTheDocument()
  })

  test('shows auto refresh toggle', async () => {
    renderApp('/settings')

    expect(await screen.findByLabelText(/auto refresh/i)).toBeInTheDocument()
  })

  test('save button exists', async () => {
    renderApp('/settings')

    expect(await screen.findByRole('button', { name: /save settings/i })).toBeInTheDocument()
  })

  test('reset button exists', async () => {
    renderApp('/settings')

    expect(await screen.findByRole('button', { name: /reset to defaults/i })).toBeInTheDocument()
  })

  test('shows saved message after save', async () => {
    const user = userEvent.setup()
    renderApp('/settings')

    const saveButton = await screen.findByRole('button', { name: /save settings/i })
    await user.click(saveButton)

    await waitFor(() => {
      expect(screen.getByText('Saved!')).toBeInTheDocument()
    })
  })
})
