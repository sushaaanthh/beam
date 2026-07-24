import { Navigate, Outlet } from 'react-router-dom'

import { Spinner } from '../components/Spinner'
import { useAuth } from '../hooks/useAuth'

export function PublicRoute() {
  const { isAuthenticated, isHydrating } = useAuth()

  if (isHydrating) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-beam-950">
        <Spinner />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}