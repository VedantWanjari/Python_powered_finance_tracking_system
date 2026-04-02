import { useEffect, useRef, useState } from 'react'
import { Search, X } from 'lucide-react'

interface TransactionSearchProps {
  value: string
  onChange: (value: string) => void
}

export default function TransactionSearch({ value, onChange }: TransactionSearchProps) {
  const [local, setLocal] = useState(value)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setLocal(value)
  }, [value])

  function handleChange(v: string) {
    setLocal(v)
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => onChange(v), 300)
  }

  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
      <input
        type="text"
        value={local}
        onChange={(e) => handleChange(e.target.value)}
        placeholder="Search transactions…"
        className="w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-9 pr-9 text-sm text-gray-900 focus:border-info-500 focus:outline-none focus:ring-1 focus:ring-info-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
      />
      {local && (
        <button
          onClick={() => handleChange('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
