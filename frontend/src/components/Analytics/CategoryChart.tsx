import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { getCategoryBreakdown } from '../../services/api'
import type { CategoryBreakdown } from '../../types'
import Loading from '../Common/Loading'
import ErrorAlert from '../Common/ErrorAlert'
import { formatCurrency, formatPercentage } from '../../utils/formatters'

const COLORS = [
  '#3b82f6', '#10b981', '#f43f5e', '#f59e0b', '#8b5cf6',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1',
]

export default function CategoryChart() {
  const [data, setData] = useState<CategoryBreakdown[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  async function fetchData() {
    setIsLoading(true)
    setError('')
    try {
      const d = await getCategoryBreakdown()
      setData(d)
    } catch {
      setError('Failed to load category data.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const chartData = data.map((d) => ({ name: d.category_name, value: d.total }))

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <h2 className="mb-4 font-semibold text-gray-900 dark:text-white">Expense by Category</h2>

      {isLoading ? (
        <Loading size="sm" />
      ) : error ? (
        <ErrorAlert error={error} onRetry={fetchData} />
      ) : data.length === 0 ? (
        <div className="py-10 text-center text-sm text-gray-400">No category data available.</div>
      ) : (
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
          <div className="flex-shrink-0">
            <ResponsiveContainer width={260} height={260}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={110}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {chartData.map((_entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => formatCurrency(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex-1 space-y-2">
            {data.map((item, idx) => (
              <div key={item.category_id ?? idx} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div
                    className="h-3 w-3 flex-shrink-0 rounded-full"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {item.category_name}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="font-medium text-gray-900 dark:text-white">
                    {formatCurrency(item.total)}
                  </span>
                  <span className="text-gray-400">{formatPercentage(item.percentage)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
