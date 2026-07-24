import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { Spinner } from '../components/Spinner'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute() {
  const { isAuthenticated, isHydrating } = useAuth()
  const location = useLocation()

  if (isHydrating) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-beam-950">
        <Spinner />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}