import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import Loading from '../Common/Loading'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return <Loading fullPage text="Checking session…" />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
