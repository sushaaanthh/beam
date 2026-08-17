import { Link } from 'react-router-dom'

import { classNames } from '../utils/classNames'

type BrandMarkProps = {
  compact?: boolean
  className?: string
}

export function BrandMark({ compact = false, className }: BrandMarkProps) {
  return (
    <Link to="/dashboard" aria-label="B.E.A.M. Dashboard" className={className}>
      <div className="flex items-center gap-2.5">
        <div
          className={classNames(
            'relative flex items-center justify-center rounded-apple-md bg-gradient-to-br from-apple-accent to-apple-accent/70 shadow-apple-md',
            compact ? 'h-8 w-8' : 'h-10 w-10',
          )}
          aria-hidden="true"
        >
          <svg
            className={classNames('text-white', compact ? 'h-5 w-5' : 'h-6 w-6')}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
          <span
            className={classNames(
              'absolute -bottom-1 -right-1 flex h-3 w-3 items-center justify-center rounded-full bg-apple-success text-[8px] font-bold',
              compact && 'hidden',
            )}
            aria-hidden="true"
          >
            B
          </span>
        </div>

        {!compact && (
          <div className="hidden sm:block">
            <span className="block text-display-sm font-semibold tracking-tight text-apple-textPrimary">
              B.E.A.M.
            </span>
            <span className="block text-caption-md text-apple-textTertiary">Behavioral Emotion Analysis Model</span>
          </div>
        )}
      </div>
    </Link>
  )
}