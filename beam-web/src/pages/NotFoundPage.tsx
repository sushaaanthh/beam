import { Link } from 'react-router-dom'

import { EmptyState } from '../components/EmptyState'
import { buttonClassName } from '../components/buttonStyles'

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-[70vh] w-full max-w-4xl items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
      <EmptyState
        className="w-full"
        eyebrow="404"
        title="This route does not exist"
        description="The page you requested was not found. Use the navigation below to return to a working part of the B.E.A.M. frontend."
        action={(
          <div className="flex flex-wrap justify-center gap-3">
            <Link to="/" className={buttonClassName('secondary')}>
              Go home
            </Link>
            <Link to="/dashboard" className={buttonClassName('primary')}>
              Open dashboard
            </Link>
          </div>
        )}
      />
    </div>
  )
}