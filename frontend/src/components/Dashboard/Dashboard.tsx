import { useCallback, useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Wallet, Activity } from 'lucide-react'
import KPICard from './KPICard'
import RecentTransactions from './RecentTransactions'
import Loading from '../Common/Loading'
import ErrorAlert from '../Common/ErrorAlert'
import { getDashboard } from '../../services/api'
import { formatCurrency } from '../../utils/formatters'
import type { DashboardData } from '../../types'

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const d = await getDashboard()
      setData(d)
    } catch {
      setError('Failed to load dashboard data.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  if (isLoading) return <Loading text="Loading dashboard…" />
  if (error) return <ErrorAlert error={error} onRetry={fetchData} />
  if (!data) return null

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KPICard
          icon={TrendingUp}
          title="Total Income"
          value={formatCurrency(data.total_income)}
          variant="green"
        />
        <KPICard
          icon={TrendingDown}
          title="Total Expenses"
          value={formatCurrency(data.total_expenses)}
          variant="red"
        />
        <KPICard
          icon={Wallet}
          title="Net Balance"
          value={formatCurrency(data.net_balance)}
          variant="blue"
        />
        <KPICard
          icon={Activity}
          title="Transactions"
          value={String(data.transaction_count)}
          variant="purple"
        />
      </div>

      {/* Recent Transactions */}
      <RecentTransactions transactions={data.recent_transactions} />
    </div>
  )
}
