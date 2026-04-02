import TrendChart from './TrendChart'
import CategoryChart from './CategoryChart'
import MonthlyReport from './MonthlyReport'

export default function Analytics() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <TrendChart />
        <CategoryChart />
      </div>
      <MonthlyReport />
    </div>
  )
}
