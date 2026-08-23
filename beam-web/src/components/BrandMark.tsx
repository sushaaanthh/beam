import { Link } from 'react-router-dom'
import { classNames } from '../utils/classNames'

type BrandMarkProps = {
  compact?: boolean
  className?: string
  to?: string
}

export function BrandMark({ compact = false, className, to = '/' }: BrandMarkProps) {
  const inner = (
    <div
      className={classNames(
        'relative flex items-center justify-center rounded-lg bg-[#141414] border border-[#2A2A2A] shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_2px_4px_rgba(0,0,0,0.6)] transition-all duration-150 group-hover:border-[#383838] group-hover:-translate-y-[1px]',
        compact ? 'h-9 w-9' : 'h-10 w-10'
      )}
      aria-hidden="true"
    >
      <img src="/logo.png" alt="B.E.A.M. logo" className="h-full w-full object-contain p-0.5" />
    </div>
  )

  const wordmark = !compact ? (
    <div className="flex flex-col">
      <span className="font-display text-xl font-bold tracking-wider text-[#F5F5F0] leading-tight group-hover:text-white">
        B.E.A.M.
      </span>
      <span className="text-[10px] tracking-[0.16em] uppercase text-[#73736F] font-medium">
        Behavioral Emotion Analysis Model
      </span>
    </div>
  ) : null

  if (to) {
    return (
      <Link to={to} aria-label="B.E.A.M. Home" className={classNames('group inline-flex items-center gap-3', className)}>
        {inner}
        {wordmark}
      </Link>
    )
  }

  return (
    <span className={classNames('group inline-flex items-center gap-3', className)}>
      {inner}
      {wordmark}
    </span>
  )
}
