import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { TrendingUp, CheckCircle, XCircle } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { validatePassword } from '../../utils/validators'
import type { ApiError } from '../../types'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { register } = useAuthStore()
  const navigate = useNavigate()

  const passwordErrors = validatePassword(password)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (passwordErrors.length > 0) {
      setError('Please meet all password requirements.')
      return
    }
    setIsLoading(true)
    try {
      await register({ username, email, password })
      navigate('/dashboard')
    } catch (err) {
      const apiErr = err as ApiError
      setError(apiErr.message ?? 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-8 dark:bg-gray-900">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-info-600">
            <TrendingUp className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create account</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Start tracking your finances</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-700 dark:bg-gray-800"
        >
          {error && (
            <div className="mb-4 rounded-lg bg-expense-50 p-3 text-sm text-expense-700 dark:bg-expense-950/30 dark:text-expense-300">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:border-info-500 focus:outline-none focus:ring-1 focus:ring-info-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="Choose a username"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:border-info-500 focus:outline-none focus:ring-1 focus:ring-info-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:border-info-500 focus:outline-none focus:ring-1 focus:ring-info-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="Create a strong password"
              />

              {/* Password requirements */}
              {password.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {[
                    { msg: 'At least 8 characters', ok: password.length >= 8 },
                    { msg: 'At least one uppercase letter', ok: /[A-Z]/.test(password) },
                    { msg: 'At least one lowercase letter', ok: /[a-z]/.test(password) },
                    { msg: 'At least one number', ok: /\d/.test(password) },
                  ].map(({ msg, ok }) => (
                    <li key={msg} className="flex items-center gap-1.5 text-xs">
                      {ok ? (
                        <CheckCircle className="h-3.5 w-3.5 text-income-500" />
                      ) : (
                        <XCircle className="h-3.5 w-3.5 text-expense-400" />
                      )}
                      <span className={ok ? 'text-income-600 dark:text-income-400' : 'text-gray-500'}>
                        {msg}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="mt-6 w-full rounded-lg bg-info-600 py-2.5 text-sm font-semibold text-white hover:bg-info-700 disabled:opacity-60"
          >
            {isLoading ? 'Creating account…' : 'Create account'}
          </button>

          <p className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-info-600 hover:underline dark:text-info-400">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
