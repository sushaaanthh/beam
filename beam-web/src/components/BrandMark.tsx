import { classNames } from '../utils/classNames'

type BrandMarkProps = {
  compact?: boolean
  className?: string
}

export function BrandMark({ compact = false, className }: BrandMarkProps) {
  return (
    <div className={classNames('flex items-center gap-3', className)}>
      <div className="kds-keycap flex h-11 w-11 items-center justify-center rounded-[14px] text-base font-semibold text-[#b2ff7d]">
        B
      </div>
      {!compact ? (
        <div>
          <p className="text-sm font-semibold tracking-[0.32em] text-white/82 uppercase">B.E.A.M.</p>
          <p className="text-sm text-white/52">Behavioral Emotion Analysis Model</p>
        </div>
      ) : null}
    </div>
  )
}
