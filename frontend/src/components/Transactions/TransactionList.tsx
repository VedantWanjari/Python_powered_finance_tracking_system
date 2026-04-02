import { useCallback, useEffect, useState } from 'react'
import { Pencil, Trash2, ChevronLeft, ChevronRight } from 'lucide-react'
import {
  getTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
} from '../../services/api'
import type { Transaction, TransactionFilters, TransactionFormData } from '../../types'
import { formatCurrency, formatDate, getTransactionTypeColor } from '../../utils/formatters'
import Loading from '../Common/Loading'
import ErrorAlert from '../Common/ErrorAlert'
import Modal from '../Common/Modal'
import TransactionForm from './TransactionForm'
import TransactionSearch from './TransactionSearch'
import TransactionFilter from './TransactionFilter'

const DEFAULT_FILTERS: TransactionFilters = {
  page: 1,
  per_page: 20,
  sort_by: 'date',
  sort_order: 'desc',
}

interface TransactionListProps {
  addModalOpen: boolean
  onAddModalClose: () => void
}

export default function TransactionList({ addModalOpen, onAddModalClose }: TransactionListProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState<TransactionFilters>(DEFAULT_FILTERS)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const [editTx, setEditTx] = useState<Transaction | null>(null)
  const [deleteTxId, setDeleteTxId] = useState<number | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const fetchTransactions = useCallback(async (f: TransactionFilters = filters) => {
    setIsLoading(true)
    setError('')
    try {
      const res = await getTransactions(f)
      setTransactions(res.items)
      setTotalPages(res.total_pages)
    } catch {
      setError('Failed to load transactions.')
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchTransactions(filters)
  }, [filters, fetchTransactions])

  function handleSearchChange(search: string) {
    setFilters((f) => ({ ...f, search, page: 1 }))
  }

  function handleFiltersChange(newFilters: TransactionFilters) {
    setFilters((f) => ({ ...f, ...newFilters }))
  }

  function resetFilters() {
    setFilters(DEFAULT_FILTERS)
  }

  async function handleCreate(data: TransactionFormData) {
    await createTransaction(data)
    onAddModalClose()
    fetchTransactions(filters)
  }

  async function handleEdit(data: TransactionFormData) {
    if (!editTx) return
    await updateTransaction(editTx.id, data)
    setEditTx(null)
    fetchTransactions(filters)
  }

  async function handleDelete() {
    if (deleteTxId === null) return
    setDeleteLoading(true)
    try {
      await deleteTransaction(deleteTxId)
      setDeleteTxId(null)
      fetchTransactions(filters)
    } catch {
      setError('Failed to delete transaction.')
    } finally {
      setDeleteLoading(false)
    }
  }

  const currentPage = filters.page ?? 1

  return (
    <div className="space-y-4">
      {/* Search */}
      <TransactionSearch value={filters.search ?? ''} onChange={handleSearchChange} />

      {/* Filters */}
      <TransactionFilter
        filters={filters}
        onChange={handleFiltersChange}
        onReset={resetFilters}
      />

      {error && <ErrorAlert error={error} onRetry={() => fetchTransactions(filters)} />}

      {/* Table */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
        {isLoading ? (
          <Loading text="Loading transactions…" />
        ) : transactions.length === 0 ? (
          <div className="py-16 text-center text-sm text-gray-400">
            No transactions found. Try adjusting your filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr className="text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3">Description</th>
                  <th className="px-5 py-3">Category</th>
                  <th className="px-5 py-3">Type</th>
                  <th className="px-5 py-3 text-right">Amount</th>
                  <th className="px-5 py-3 text-right">Actions</th>
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
                    <td className="px-5 py-3">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${
                          t.transaction_type === 'income'
                            ? 'bg-income-100 text-income-700 dark:bg-income-900/30 dark:text-income-300'
                            : 'bg-expense-100 text-expense-700 dark:bg-expense-900/30 dark:text-expense-300'
                        }`}
                      >
                        {t.transaction_type}
                      </span>
                    </td>
                    <td
                      className={`px-5 py-3 text-right text-sm font-semibold ${getTransactionTypeColor(t.transaction_type)}`}
                    >
                      {t.transaction_type === 'income' ? '+' : '-'}
                      {formatCurrency(t.amount)}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => setEditTx(t)}
                          className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-info-600 dark:hover:bg-gray-700"
                          title="Edit"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => setDeleteTxId(t.id)}
                          className="rounded p-1.5 text-gray-400 hover:bg-expense-50 hover:text-expense-600 dark:hover:bg-gray-700"
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {!isLoading && totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-gray-200 px-5 py-3 dark:border-gray-700">
            <button
              onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))}
              disabled={currentPage <= 1}
              className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-40 dark:text-gray-400 dark:hover:bg-gray-700"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))}
              disabled={currentPage >= totalPages}
              className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-40 dark:text-gray-400 dark:hover:bg-gray-700"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {/* Add Modal */}
      <Modal isOpen={addModalOpen} onClose={onAddModalClose} title="Add Transaction">
        <TransactionForm onSubmit={handleCreate} onCancel={onAddModalClose} />
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={!!editTx} onClose={() => setEditTx(null)} title="Edit Transaction">
        {editTx && (
          <TransactionForm
            transaction={editTx}
            onSubmit={handleEdit}
            onCancel={() => setEditTx(null)}
          />
        )}
      </Modal>

      {/* Delete Confirmation */}
      <Modal isOpen={deleteTxId !== null} onClose={() => setDeleteTxId(null)} title="Delete Transaction" maxWidth="max-w-sm">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Are you sure you want to delete this transaction? This action cannot be undone.
        </p>
        <div className="mt-5 flex gap-3">
          <button
            onClick={() => setDeleteTxId(null)}
            className="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteLoading}
            className="flex-1 rounded-lg bg-expense-600 py-2.5 text-sm font-semibold text-white hover:bg-expense-700 disabled:opacity-60"
          >
            {deleteLoading ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </Modal>
    </div>
  )
}
