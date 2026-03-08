import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginPage from './LoginPage'
import { useAuthStore } from './authStore'

vi.mock('./authStore')

const mockLogin = vi.fn()

beforeEach(() => {
  vi.mocked(useAuthStore).mockReturnValue({
    login: mockLogin,
    token: null,
    profile: null,
    logout: vi.fn(),
    fetchMe: vi.fn(),
  })
  mockLogin.mockReset()
})

describe('LoginPage', () => {
  it('renders username, password fields and a submit button', () => {
    render(<LoginPage />)
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('calls login with the entered credentials on submit', async () => {
    mockLogin.mockResolvedValue(undefined)
    render(<LoginPage />)

    await userEvent.type(screen.getByLabelText(/username/i), 'admin')
    await userEvent.type(screen.getByLabelText(/password/i), 'password123')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('admin', 'password123')
    })
  })

  it('shows a loading state while logging in', async () => {
    // Never resolves so we can inspect the pending state
    mockLogin.mockReturnValue(new Promise(() => {}))
    render(<LoginPage />)

    await userEvent.type(screen.getByLabelText(/username/i), 'admin')
    await userEvent.type(screen.getByLabelText(/password/i), 'pass')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))

    expect(screen.getByRole('button', { name: /signing in/i })).toBeDisabled()
  })

  it('displays the error detail from the API on login failure', async () => {
    mockLogin.mockRejectedValue({
      response: { data: { detail: 'Invalid username or password' } },
    })
    render(<LoginPage />)

    await userEvent.type(screen.getByLabelText(/username/i), 'admin')
    await userEvent.type(screen.getByLabelText(/password/i), 'wrongpass')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('Invalid username or password')).toBeInTheDocument()
    })
  })

  it('falls back to a generic message if the API gives no detail', async () => {
    mockLogin.mockRejectedValue(new Error('Network Error'))
    render(<LoginPage />)

    await userEvent.type(screen.getByLabelText(/username/i), 'admin')
    await userEvent.type(screen.getByLabelText(/password/i), 'pass')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('Invalid username or password')).toBeInTheDocument()
    })
  })
})
