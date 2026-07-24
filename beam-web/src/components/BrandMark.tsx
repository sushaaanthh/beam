import { classNames } from '../utils/classNames'

type BrandMarkProps = {
  compact?: boolean
  className?: string
}

export function BrandMark({ compact = false, className }: BrandMarkProps) {
  return (
    <div className={classNames('flex items-center gap-3', className)}>
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-sky-500 to-indigo-500 text-base font-semibold text-white shadow-glow">
        B
      </div>
      {!compact ? (
        <div>
          <p className="text-sm font-semibold tracking-[0.28em] text-slate-400 uppercase">B.E.A.M.</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">Behavioral Emotion Analysis Model</p>
        </div>
      ) : null}
    </div>
  )
}