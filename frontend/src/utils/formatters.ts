import { format, parseISO } from 'date-fns'

export function formatCurrency(amount: number, currency = 'INR'): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatDate(date: string): string {
  try {
    return format(parseISO(date), 'MMM d, yyyy')
  } catch {
    return date
  }
}

export function formatDateInput(date: string): string {
  try {
    return format(parseISO(date), 'yyyy-MM-dd')
  } catch {
    return date
  }
}

export function formatMonth(month: string): string {
  try {
    return format(parseISO(`${month}-01`), 'MMM yyyy')
  } catch {
    return month
  }
}

export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

export function getTransactionTypeColor(type: string): string {
  return type === 'income'
    ? 'text-income-600 dark:text-income-400'
    : 'text-expense-600 dark:text-expense-400'
}

export function getCategoryIcon(icon: string | null | undefined): string {
  return icon ?? '💼'
}
