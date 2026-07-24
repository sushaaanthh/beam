import { Link } from 'react-router-dom'

import { buttonClassName } from '../components/buttonStyles'
import { Card } from '../components/Card'

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-[70vh] w-full max-w-4xl items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
      <Card className="w-full space-y-6 p-10 text-center">
        <p className="text-xs font-semibold tracking-[0.32em] text-cyan-700 uppercase dark:text-cyan-300">404</p>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">This route does not exist</h1>
        <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
          The page you requested was not found. Use the navigation below to return to a working part of the B.E.A.M. frontend.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link to="/" className={buttonClassName('secondary')}>
            Go home
          </Link>
          <Link to="/dashboard" className={buttonClassName('primary')}>
            Open dashboard
          </Link>
        </div>
      </Card>
    </div>
  )
}