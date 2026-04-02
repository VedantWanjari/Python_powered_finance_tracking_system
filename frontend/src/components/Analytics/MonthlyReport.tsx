import { useCallback, useEffect, useState } from 'react'
import { getTrends } from '../../services/api'
import type { TrendData } from '../../types'
import Loading from '../Common/Loading'
import ErrorAlert from '../Common/ErrorAlert'
import { formatCurrency, formatMonth } from '../../utils/formatters'
import { useAuthStore } from '../../store/authStore'
import clsx from 'clsx'

export default function MonthlyReport() {
  const [data, setData] = useState<TrendData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuthStore()

  const canView = user?.role === 'analyst' || user?.role === 'admin'

  const fetchData = useCallback(async () => {
    if (!canView) return
    setIsLoading(true)
    setError('')
    try {
      const d = await getTrends(12)
      setData([...d].reverse())
    } catch {
      setError('Failed to load monthly report.')
    } finally {
      setIsLoading(false)
    }
  }, [canView])

  useEffect(() => { fetchData() }, [fetchData])

  if (!canView) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-6 text-center text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400">
        Monthly report requires Analyst or Admin role.
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
        <h2 className="font-semibold text-gray-900 dark:text-white">Monthly Summary</h2>
      </div>

      {isLoading ? (
        <Loading size="sm" />
      ) : error ? (
        <ErrorAlert error={error} onRetry={fetchData} />
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr className="text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                <th className="px-5 py-3">Month</th>
                <th className="px-5 py-3 text-right">Income</th>
                <th className="px-5 py-3 text-right">Expenses</th>
                <th className="px-5 py-3 text-right">Net</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50">
              {data.map((row) => (
                <tr key={row.month} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="px-5 py-3 text-sm font-medium text-gray-900 dark:text-white">
                    {formatMonth(row.month)}
                  </td>
                  <td className="px-5 py-3 text-right text-sm text-income-600 dark:text-income-400">
                    +{formatCurrency(row.income)}
                  </td>
                  <td className="px-5 py-3 text-right text-sm text-expense-600 dark:text-expense-400">
                    -{formatCurrency(row.expenses)}
                  </td>
                  <td
                    className={clsx(
                      'px-5 py-3 text-right text-sm font-semibold',
                      row.net >= 0
                        ? 'text-income-600 dark:text-income-400'
                        : 'text-expense-600 dark:text-expense-400',
                    )}
                  >
                    {row.net >= 0 ? '+' : ''}
                    {formatCurrency(row.net)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
