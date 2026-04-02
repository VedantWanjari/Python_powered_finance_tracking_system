import { useState, type FormEvent } from 'react'
import { User, Mail, Lock, Save } from 'lucide-react'
import MainLayout from '../components/Layout/MainLayout'
import { useAuthStore } from '../store/authStore'
import type { ApiError } from '../types'
import { formatDate } from '../utils/formatters'

export default function ProfilePage() {
  const { user, updateMe, updatePassword } = useAuthStore()

  const [profileForm, setProfileForm] = useState({
    username: user?.username ?? '',
    email: user?.email ?? '',
  })
  const [profileSuccess, setProfileSuccess] = useState('')
  const [profileError, setProfileError] = useState('')
  const [profileLoading, setProfileLoading] = useState(false)

  const [pwForm, setPwForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [pwSuccess, setPwSuccess] = useState('')
  const [pwError, setPwError] = useState('')
  const [pwLoading, setPwLoading] = useState(false)

  async function handleProfileSubmit(e: FormEvent) {
    e.preventDefault()
    setProfileError('')
    setProfileSuccess('')
    setProfileLoading(true)
    try {
      await updateMe({ username: profileForm.username, email: profileForm.email })
      setProfileSuccess('Profile updated successfully.')
    } catch (err) {
      setProfileError((err as ApiError).message ?? 'Update failed.')
    } finally {
      setProfileLoading(false)
    }
  }

  async function handlePasswordSubmit(e: FormEvent) {
    e.preventDefault()
    setPwError('')
    setPwSuccess('')
    if (pwForm.new_password !== pwForm.confirm_password) {
      setPwError('New passwords do not match.')
      return
    }
    setPwLoading(true)
    try {
      await updatePassword({
        current_password: pwForm.current_password,
        new_password: pwForm.new_password,
      })
      setPwSuccess('Password changed successfully.')
      setPwForm({ current_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      setPwError((err as ApiError).message ?? 'Password change failed.')
    } finally {
      setPwLoading(false)
    }
  }

  const inputClass =
    'w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:border-info-500 focus:outline-none focus:ring-1 focus:ring-info-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white'

  return (
    <MainLayout>
      <div className="mx-auto max-w-2xl space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile</h1>

        {/* User Info */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-info-100 dark:bg-info-900/30">
              <User className="h-8 w-8 text-info-600 dark:text-info-400" />
            </div>
            <div>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{user?.username}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
              <span className="mt-1 inline-flex rounded-full bg-info-100 px-2.5 py-0.5 text-xs font-medium capitalize text-info-700 dark:bg-info-900/30 dark:text-info-300">
                {user?.role}
              </span>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 border-t border-gray-100 pt-4 dark:border-gray-700">
            <div>
              <p className="text-xs text-gray-400">Member since</p>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {user?.created_at ? formatDate(user.created_at) : '—'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Last updated</p>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {user?.updated_at ? formatDate(user.updated_at) : '—'}
              </p>
            </div>
          </div>
        </div>

        {/* Edit Profile */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <h2 className="mb-4 flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
            <Mail className="h-4 w-4" /> Edit Profile
          </h2>

          {profileSuccess && (
            <div className="mb-4 rounded-lg bg-income-50 p-3 text-sm text-income-700 dark:bg-income-900/20 dark:text-income-300">
              {profileSuccess}
            </div>
          )}
          {profileError && (
            <div className="mb-4 rounded-lg bg-expense-50 p-3 text-sm text-expense-700 dark:bg-expense-950/30 dark:text-expense-300">
              {profileError}
            </div>
          )}

          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Username
              </label>
              <input
                type="text"
                value={profileForm.username}
                onChange={(e) => setProfileForm((f) => ({ ...f, username: e.target.value }))}
                className={inputClass}
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email
              </label>
              <input
                type="email"
                value={profileForm.email}
                onChange={(e) => setProfileForm((f) => ({ ...f, email: e.target.value }))}
                className={inputClass}
              />
            </div>
            <button
              type="submit"
              disabled={profileLoading}
              className="flex items-center gap-2 rounded-lg bg-info-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-info-700 disabled:opacity-60"
            >
              <Save className="h-4 w-4" />
              {profileLoading ? 'Saving…' : 'Save Changes'}
            </button>
          </form>
        </div>

        {/* Change Password */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <h2 className="mb-4 flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
            <Lock className="h-4 w-4" /> Change Password
          </h2>

          {pwSuccess && (
            <div className="mb-4 rounded-lg bg-income-50 p-3 text-sm text-income-700 dark:bg-income-900/20 dark:text-income-300">
              {pwSuccess}
            </div>
          )}
          {pwError && (
            <div className="mb-4 rounded-lg bg-expense-50 p-3 text-sm text-expense-700 dark:bg-expense-950/30 dark:text-expense-300">
              {pwError}
            </div>
          )}

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Current Password
              </label>
              <input
                type="password"
                value={pwForm.current_password}
                onChange={(e) => setPwForm((f) => ({ ...f, current_password: e.target.value }))}
                className={inputClass}
                autoComplete="current-password"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                New Password
              </label>
              <input
                type="password"
                value={pwForm.new_password}
                onChange={(e) => setPwForm((f) => ({ ...f, new_password: e.target.value }))}
                className={inputClass}
                autoComplete="new-password"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Confirm New Password
              </label>
              <input
                type="password"
                value={pwForm.confirm_password}
                onChange={(e) => setPwForm((f) => ({ ...f, confirm_password: e.target.value }))}
                className={inputClass}
                autoComplete="new-password"
              />
            </div>
            <button
              type="submit"
              disabled={pwLoading}
              className="flex items-center gap-2 rounded-lg bg-info-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-info-700 disabled:opacity-60"
            >
              <Lock className="h-4 w-4" />
              {pwLoading ? 'Changing…' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </MainLayout>
  )
}
