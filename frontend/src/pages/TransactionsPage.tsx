import { useState } from 'react'
import { Plus } from 'lucide-react'
import MainLayout from '../components/Layout/MainLayout'
import TransactionList from '../components/Transactions/TransactionList'

export default function TransactionsPage() {
  const [addOpen, setAddOpen] = useState(false)

  return (
    <MainLayout>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Transactions</h1>
          <button
            onClick={() => setAddOpen(true)}
            className="flex items-center gap-2 rounded-xl bg-info-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-info-700"
          >
            <Plus className="h-4 w-4" />
            Add Transaction
          </button>
        </div>
        <TransactionList addModalOpen={addOpen} onAddModalClose={() => setAddOpen(false)} />
      </div>
    </MainLayout>
  )
}
