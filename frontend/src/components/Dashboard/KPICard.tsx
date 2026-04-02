import clsx from 'clsx'
import type { LucideIcon } from 'lucide-react'

type Variant = 'green' | 'red' | 'blue' | 'purple'

interface KPICardProps {
  icon: LucideIcon
  title: string
  value: string
  change?: number
  variant?: Variant
}

const variantStyles: Record<Variant, { bg: string; icon: string; badge: string }> = {
  green: {
    bg: 'bg-income-50 dark:bg-income-900/20',
    icon: 'text-income-600 dark:text-income-400',
    badge: 'bg-income-100 text-income-700 dark:bg-income-800 dark:text-income-300',
  },
  red: {
    bg: 'bg-expense-50 dark:bg-expense-900/20',
    icon: 'text-expense-600 dark:text-expense-400',
    badge: 'bg-expense-100 text-expense-700 dark:bg-expense-800 dark:text-expense-300',
  },
  blue: {
    bg: 'bg-info-50 dark:bg-info-900/20',
    icon: 'text-info-600 dark:text-info-400',
    badge: 'bg-info-100 text-info-700 dark:bg-info-800 dark:text-info-300',
  },
  purple: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    icon: 'text-purple-600 dark:text-purple-400',
    badge: 'bg-purple-100 text-purple-700 dark:bg-purple-800 dark:text-purple-300',
  },
}

export default function KPICard({
  icon: Icon,
  title,
  value,
  change,
  variant = 'blue',
}: KPICardProps) {
  const styles = variantStyles[variant]

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-start justify-between">
        <div className={clsx('rounded-lg p-2.5', styles.bg)}>
          <Icon className={clsx('h-6 w-6', styles.icon)} />
        </div>
        {change !== undefined && (
          <span className={clsx('rounded-full px-2 py-0.5 text-xs font-semibold', styles.badge)}>
            {change >= 0 ? '+' : ''}
            {change.toFixed(1)}%
          </span>
        )}
      </div>
      <p className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{title}</p>
    </div>
  )
}
