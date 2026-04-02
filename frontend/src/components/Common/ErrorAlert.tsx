import { AlertCircle, RefreshCw, X } from 'lucide-react'

interface ErrorAlertProps {
  error: string
  onRetry?: () => void
  onDismiss?: () => void
}

export default function ErrorAlert({ error, onRetry, onDismiss }: ErrorAlertProps) {
  return (
    <div className="rounded-lg border border-expense-200 bg-expense-50 p-4 dark:border-expense-800 dark:bg-expense-950/30">
      <div className="flex items-start gap-3">
        <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-expense-500" />
        <p className="flex-1 text-sm text-expense-700 dark:text-expense-300">{error}</p>
        <div className="flex gap-1">
          {onRetry && (
            <button
              onClick={onRetry}
              className="rounded p-1 text-expense-500 hover:bg-expense-100 dark:hover:bg-expense-900"
              title="Retry"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="rounded p-1 text-expense-500 hover:bg-expense-100 dark:hover:bg-expense-900"
              title="Dismiss"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
