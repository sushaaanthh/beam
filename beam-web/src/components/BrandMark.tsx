import { classNames } from '../utils/classNames'

type BrandMarkProps = {
  compact?: boolean
  className?: string
}

export function BrandMark({ compact = false, className }: BrandMarkProps) {
  return (
    <div className={classNames('flex items-center gap-3', className)}>
      <div className="flex h-11 w-11 items-center justify-center rounded-[1rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.09),rgba(255,255,255,0.03))] text-base font-semibold text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_12px_24px_rgba(0,0,0,0.45)]">
        B
      </div>
      {!compact ? (
        <div>
          <p className="text-sm font-semibold tracking-[0.32em] text-white/74 uppercase">B.E.A.M.</p>
          <p className="text-sm text-white/52">Behavioral Emotion Analysis Model</p>
        </div>
      ) : null}
    </div>
  )
}