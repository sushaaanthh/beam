import { Link } from 'react-router-dom'
import { AlertTriangle, ArrowLeft, LayoutDashboard } from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-lg items-center justify-center p-4">
      <Card variant="default" padding="none" className="p-8 text-center space-y-5 w-full">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-[#141414] border border-[#262626] text-[#C7FF4A]">
          <AlertTriangle className="h-6 w-6" />
        </div>

        <div>
          <span className="text-[10px] font-mono text-[#73736F] uppercase">
            ERROR 404 // UNROUTED_ENDPOINT
          </span>
          <h2 className="font-display text-2xl font-bold text-[#F5F5F0] mt-1">
            ROUTE NOT FOUND
          </h2>
          <p className="text-xs text-[#73736F] mt-1">
            The requested path does not exist in the B.E.A.M. instrument routing matrix.
          </p>
        </div>

        <div className="pt-2 flex flex-wrap justify-center gap-3">
          <Link to="/">
            <Button variant="secondary" size="sm" leftIcon={<ArrowLeft className="h-3.5 w-3.5" />}>
              Return Home
            </Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="primary" size="sm" leftIcon={<LayoutDashboard className="h-3.5 w-3.5" />}>
              Dashboard
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  )
}