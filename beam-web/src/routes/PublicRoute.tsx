import { Navigate, Outlet } from 'react-router-dom'

import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { useAuth } from '../hooks/useAuth'

export function PublicRoute() {
  const { isAuthenticated, isHydrating } = useAuth()

  if (isHydrating) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505] px-4">
        <LoadingSkeleton className="w-full max-w-md" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}