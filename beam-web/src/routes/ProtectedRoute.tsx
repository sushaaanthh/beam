import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute() {
  const { isAuthenticated, isHydrating } = useAuth()
  const location = useLocation()

  if (isHydrating) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505] px-4">
        <LoadingSkeleton className="w-full max-w-md" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}