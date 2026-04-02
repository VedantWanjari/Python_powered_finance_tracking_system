import { useEffect, useState, type FormEvent } from 'react'
import { getCategories } from '../../services/api'
import type { Transaction, Category, TransactionFormData } from '../../types'
import { formatDateInput } from '../../utils/formatters'
import { validateAmount } from '../../utils/validators'

interface TransactionFormProps {
  transaction?: Transaction
  onSubmit: (data: TransactionFormData) => Promise<void>
  onCancel: () => void
}

const defaultForm: TransactionFormData = {
  amount: '',
  transaction_type: 'expense',
  date: new Date().toISOString().slice(0, 10),
  description: '',
  category_id: '',
  notes: '',
  tags: '',
  is_recurring: false,
  recurring_frequency: '',
  budget_month: '',
}

export default function TransactionForm({ transaction, onSubmit, onCancel }: TransactionFormProps) {
  const [form, setForm] = useState<TransactionFormData>(() =>
    transaction
      ? {
          amount: String(transaction.amount),
          transaction_type: transaction.transaction_type,
          date: formatDateInput(transaction.date),
          description: transaction.description,
          category_id: transaction.category_id ?? '',
          notes: transaction.notes ?? '',
          tags: transaction.tags?.join(', ') ?? '',
          is_recurring: transaction.is_recurring,
          recurring_frequency: transaction.recurring_frequency ?? '',
          budget_month: transaction.budget_month ?? '',
        }
      : defaultForm,
  )
  const [categories, setCategories] = useState<Category[]>([])
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [apiError, setApiError] = useState('')

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => {})
  }, [])

  function set(partial: Partial<TransactionFormData>) {
    setForm((f) => ({ ...f, ...partial }))
  }

  function validate(): boolean {
    const errs: Record<string, string> = {}
    if (!validateAmount(form.amount)) errs.amount = 'Please enter a valid positive amount.'
    if (!form.description.trim()) errs.description = 'Description is required.'
    if (!form.date) errs.date = 'Date is required.'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!validate()) return
    setIsLoading(true)
    setApiError('')
    try {
      await onSubmit(form)
    } catch (err) {
      const e = err as { message?: string }
      setApiError(e.message ?? 'An error occurred.')
    } finally {
      setIsLoading(false)
    }
  }

  const inputClass =
    'w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:border-info-500 focus:outline-none focus:ring-1 focus:ring-info-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white'

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {apiError && (
        <div className="rounded-lg bg-expense-50 p-3 text-sm text-expense-700 dark:bg-expense-950/30 dark:text-expense-300">
          {apiError}
        </div>
      )}

      {/* Amount + Type */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Amount *
          </label>
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={form.amount}
            onChange={(e) => set({ amount: e.target.value })}
            className={inputClass}
            placeholder="0.00"
          />
          {errors.amount && <p className="mt-1 text-xs text-expense-500">{errors.amount}</p>}
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Type *
          </label>
          <div className="flex rounded-lg border border-gray-300 overflow-hidden dark:border-gray-600">
            {(['expense', 'income'] as const).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => set({ transaction_type: type })}
                className={`flex-1 py-2.5 text-sm font-medium capitalize transition-colors ${
                  form.transaction_type === type
                    ? type === 'income'
                      ? 'bg-income-500 text-white'
                      : 'bg-expense-500 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Date */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Date *
        </label>
        <input
          type="date"
          value={form.date}
          onChange={(e) => set({ date: e.target.value })}
          className={inputClass}
        />
        {errors.date && <p className="mt-1 text-xs text-expense-500">{errors.date}</p>}
      </div>

      {/* Description */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Description *
        </label>
        <input
          type="text"
          value={form.description}
          onChange={(e) => set({ description: e.target.value })}
          className={inputClass}
          placeholder="What was this for?"
        />
        {errors.description && (
          <p className="mt-1 text-xs text-expense-500">{errors.description}</p>
        )}
      </div>

      {/* Category */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Category
        </label>
        <select
          value={form.category_id ?? ''}
          onChange={(e) => set({ category_id: e.target.value ? Number(e.target.value) : '' })}
          className={inputClass}
        >
          <option value="">No category</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.icon ? `${c.icon} ` : ''}
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {/* Notes */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Notes
        </label>
        <textarea
          value={form.notes}
          onChange={(e) => set({ notes: e.target.value })}
          rows={2}
          className={inputClass}
          placeholder="Optional notes…"
        />
      </div>

      {/* Tags */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Tags <span className="text-xs text-gray-400">(comma-separated)</span>
        </label>
        <input
          type="text"
          value={form.tags}
          onChange={(e) => set({ tags: e.target.value })}
          className={inputClass}
          placeholder="food, travel, utilities"
        />
      </div>

      {/* Budget Month */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Budget Month
        </label>
        <input
          type="month"
          value={form.budget_month}
          onChange={(e) => set({ budget_month: e.target.value })}
          className={inputClass}
        />
      </div>

      {/* Recurring */}
      <div className="flex items-center gap-3">
        <input
          id="recurring"
          type="checkbox"
          checked={form.is_recurring}
          onChange={(e) => set({ is_recurring: e.target.checked })}
          className="h-4 w-4 rounded border-gray-300 text-info-600 focus:ring-info-500"
        />
        <label htmlFor="recurring" className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Recurring transaction
        </label>
      </div>

      {form.is_recurring && (
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Frequency
          </label>
          <select
            value={form.recurring_frequency}
            onChange={(e) => set({ recurring_frequency: e.target.value })}
            className={inputClass}
          >
            <option value="">Select frequency</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
      )}

      {/* Buttons */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 rounded-lg bg-info-600 py-2.5 text-sm font-semibold text-white hover:bg-info-700 disabled:opacity-60"
        >
          {isLoading ? 'Saving…' : transaction ? 'Update' : 'Create'}
        </button>
      </div>
    </form>
  )
}
