import { Link } from 'react-router-dom'
import { classNames } from '../utils/classNames'

type BrandMarkProps = {
  compact?: boolean
  className?: string
  to?: string
}

export function BrandMark({ compact = false, className, to = '/' }: BrandMarkProps) {
  return (
    <Link to={to} aria-label="B.E.A.M. Home" className={classNames('group inline-flex items-center gap-3', className)}>
      <div
        className={classNames(
          'relative flex items-center justify-center rounded-lg bg-[#141414] border border-[#2A2A2A] shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_2px_4px_rgba(0,0,0,0.6)] transition-all duration-150 group-hover:border-[#383838] group-hover:-translate-y-[1px]',
          compact ? 'h-9 w-9' : 'h-10 w-10'
        )}
        aria-hidden="true"
      >
        <span className="font-display text-[#C7FF4A] text-lg font-bold tracking-wider">
          B
        </span>
        <span className="absolute -top-1 -right-1 flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#C7FF4A] opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-[#C7FF4A]"></span>
        </span>
      </div>

      {!compact && (
        <div className="flex flex-col">
          <span className="font-display text-xl font-bold tracking-wider text-[#F5F5F0] leading-tight group-hover:text-white">
            B.E.A.M.
          </span>
          <span className="text-[10px] tracking-[0.16em] uppercase text-[#73736F] font-medium">
            Behavioral Emotion Analysis Model
          </span>
        </div>
      )}
    </Link>
  )
}