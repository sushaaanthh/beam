import { classNames } from '../../utils/classNames'

type MetricDisplayProps = {
  value: string
  label: string
  /** 'lime' highlights the value with the accent — use sparingly. */
  tone?: 'chalk' | 'lime'
  className?: string
}

export function MetricDisplay({ value, label, tone = 'chalk', className }: MetricDisplayProps) {
  return (
    <div className={classNames('flex flex-col gap-1', className)}>
      <span
        className={classNames(
          'font-display text-2xl font-semibold leading-none sm:text-3xl',
          tone === 'lime' ? 'text-lime' : 'text-chalk',
        )}
      >
        {value}
      </span>
      <span className="text-[10px] font-medium uppercase tracking-[0.16em] text-dim">
        {label}
      </span>
    </div>
  )
}
