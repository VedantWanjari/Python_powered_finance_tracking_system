import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { TrendingUp, BarChart2, Shield, Zap } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const features = [
  {
    icon: TrendingUp,
    title: 'Track Everything',
    desc: 'Record income and expenses with categories, tags, and notes.',
  },
  {
    icon: BarChart2,
    title: 'Visual Analytics',
    desc: 'Interactive charts to understand your spending patterns.',
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    desc: 'Session-based authentication keeps your data safe.',
  },
  {
    icon: Zap,
    title: 'Fast & Responsive',
    desc: 'Built with React 18 and Vite for a blazing-fast experience.',
  },
]

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && isAuthenticated) navigate('/dashboard')
  }, [isAuthenticated, isLoading, navigate])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 py-24 text-center">
        <div className="mb-6 flex justify-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-info-600 shadow-lg">
            <TrendingUp className="h-11 w-11 text-white" />
          </div>
        </div>
        <h1 className="mb-4 text-5xl font-extrabold text-gray-900 dark:text-white">
          Finance Tracker
        </h1>
        <p className="mb-10 text-xl text-gray-500 dark:text-gray-400">
          Take control of your personal finances with powerful tracking, analytics, and insights.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            to="/register"
            className="rounded-xl bg-info-600 px-8 py-3 font-semibold text-white shadow hover:bg-info-700"
          >
            Get started free
          </Link>
          <Link
            to="/login"
            className="rounded-xl border border-gray-300 bg-white px-8 py-3 font-semibold text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
          >
            Sign in
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-6 pb-24">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div
              key={title}
              className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
            >
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-info-50 dark:bg-info-900/20">
                <Icon className="h-6 w-6 text-info-600 dark:text-info-400" />
              </div>
              <h3 className="mb-1.5 font-semibold text-gray-900 dark:text-white">{title}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
