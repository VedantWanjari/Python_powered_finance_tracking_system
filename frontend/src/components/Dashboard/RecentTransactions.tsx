import { Link } from 'react-router-dom'
import type { Transaction } from '../../types'
import { formatCurrency, formatDate, getTransactionTypeColor } from '../../utils/formatters'
import { ArrowRight } from 'lucide-react'

interface RecentTransactionsProps {
  transactions: Transaction[]
}

export default function RecentTransactions({ transactions }: RecentTransactionsProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4 dark:border-gray-700">
        <h2 className="font-semibold text-gray-900 dark:text-white">Recent Transactions</h2>
        <Link
          to="/transactions"
          className="flex items-center gap-1 text-sm text-info-600 hover:underline dark:text-info-400"
        >
          View all <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {transactions.length === 0 ? (
        <div className="py-10 text-center text-sm text-gray-400">No transactions yet.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr className="text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3">Description</th>
                <th className="px-5 py-3">Category</th>
                <th className="px-5 py-3 text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50">
              {transactions.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="whitespace-nowrap px-5 py-3 text-sm text-gray-500 dark:text-gray-400">
                    {formatDate(t.date)}
                  </td>
                  <td className="px-5 py-3 text-sm font-medium text-gray-900 dark:text-white">
                    {t.description}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-500 dark:text-gray-400">
                    {t.category_name ?? '—'}
                  </td>
                  <td
                    className={`px-5 py-3 text-right text-sm font-semibold ${getTransactionTypeColor(t.transaction_type)}`}
                  >
                    {t.transaction_type === 'income' ? '+' : '-'}
                    {formatCurrency(t.amount)}
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
