import { useNavigate } from 'react-router-dom'
import { Home } from 'lucide-react'

export default function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-gray-50 px-6 text-center dark:bg-gray-900">
      <p className="text-8xl font-extrabold text-gray-200 dark:text-gray-700">404</p>
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Page not found</h1>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          Sorry, we couldn&apos;t find the page you&apos;re looking for.
        </p>
      </div>
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 rounded-xl bg-info-600 px-6 py-2.5 font-semibold text-white hover:bg-info-700"
      >
        <Home className="h-4 w-4" />
        Go back
      </button>
    </div>
  )
}
