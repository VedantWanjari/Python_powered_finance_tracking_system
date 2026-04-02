import { useCallback, useEffect, useState } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { getTrends } from '../../services/api'
import type { TrendData } from '../../types'
import Loading from '../Common/Loading'
import ErrorAlert from '../Common/ErrorAlert'
import { formatMonth } from '../../utils/formatters'
import { useAuthStore } from '../../store/authStore'

export default function TrendChart() {
  const [data, setData] = useState<TrendData[]>([])
  const [months, setMonths] = useState(6)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuthStore()

  const canView = user?.role === 'analyst' || user?.role === 'admin'

  const fetchData = useCallback(async () => {
    if (!canView) return
    setIsLoading(true)
    setError('')
    try {
      const d = await getTrends(months)
      setData(d.map((item) => ({ ...item, month: formatMonth(item.month) })))
    } catch {
      setError('Failed to load trend data.')
    } finally {
      setIsLoading(false)
    }
  }, [canView, months])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  if (!canView) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-6 text-center text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400">
        Trend analytics require Analyst or Admin role.
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-gray-900 dark:text-white">Income vs Expenses Trend</h2>
        <select
          value={months}
          onChange={(e) => setMonths(Number(e.target.value))}
          className="rounded-lg border border-gray-300 px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
        >
          <option value={3}>3 months</option>
          <option value={6}>6 months</option>
          <option value={12}>12 months</option>
        </select>
      </div>

      {isLoading ? (
        <Loading size="sm" />
      ) : error ? (
        <ErrorAlert error={error} onRetry={fetchData} />
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v: number) => `₹${v.toLocaleString('en-IN')}`} />
            <Legend />
            <Area
              type="monotone"
              dataKey="income"
              stroke="#10b981"
              fill="url(#incomeGrad)"
              name="Income"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="expenses"
              stroke="#f43f5e"
              fill="url(#expenseGrad)"
              name="Expenses"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
