import { useEffect, useState } from 'react'
import { Filter, ChevronDown, ChevronUp } from 'lucide-react'
import type { TransactionFilters, Category } from '../../types'
import { getCategories } from '../../services/api'

interface TransactionFilterProps {
  filters: TransactionFilters
  onChange: (filters: TransactionFilters) => void
  onReset: () => void
}

export default function TransactionFilter({ filters, onChange, onReset }: TransactionFilterProps) {
  const [open, setOpen] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => {})
  }, [])

  function set(partial: Partial<TransactionFilters>) {
    onChange({ ...filters, ...partial, page: 1 })
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-200"
      >
        <span className="flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filters
        </span>
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {open && (
        <div className="border-t border-gray-200 px-4 pb-4 pt-3 dark:border-gray-700">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {/* Date From */}
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Date From
              </label>
              <input
                type="date"
                value={filters.date_from ?? ''}
                onChange={(e) => set({ date_from: e.target.value || undefined })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-info-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Date To
              </label>
              <input
                type="date"
                value={filters.date_to ?? ''}
                onChange={(e) => set({ date_to: e.target.value || undefined })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-info-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Type */}
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Type
              </label>
              <select
                value={filters.transaction_type ?? ''}
                onChange={(e) =>
                  set({
                    transaction_type: (e.target.value as TransactionFilters['transaction_type']) || '',
                  })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-info-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All</option>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Category
              </label>
              <select
                value={filters.category_id ?? ''}
                onChange={(e) => set({ category_id: e.target.value ? Number(e.target.value) : '' })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-info-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Amount Min */}
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Min Amount
              </label>
              <input
                type="number"
                min={0}
                value={filters.amount_min ?? ''}
                onChange={(e) => set({ amount_min: e.target.value ? Number(e.target.value) : '' })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-info-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="0"
              />
            </div>

            {/* Amount Max */}
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Max Amount
              </label>
              <input
                type="number"
                min={0}
                value={filters.amount_max ?? ''}
                onChange={(e) => set({ amount_max: e.target.value ? Number(e.target.value) : '' })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-info-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="∞"
              />
            </div>
          </div>

          <div className="mt-3 flex justify-end gap-2">
            <button
              onClick={onReset}
              className="rounded-lg border border-gray-300 px-4 py-1.5 text-sm text-gray-600 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
            >
              Reset
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
