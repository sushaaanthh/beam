import { classNames } from '../../utils/classNames'

type StatusIndicatorProps = {
  label: string
  tone?: 'operational' | 'idle' | 'offline'
  pulse?: boolean
  className?: string
}

const dotColors = {
  operational: 'bg-lime',
  idle: 'bg-[#8E8E8A]',
  offline: 'bg-[#6E3A3A]',
}

export function StatusIndicator({ label, tone = 'operational', pulse = true, className }: StatusIndicatorProps) {
  return (
    <span
      className={classNames('inline-flex items-center gap-2', className)}
      role="status"
      aria-label={`Status: ${label}`}
    >
      <span className="relative flex h-1.5 w-1.5" aria-hidden="true">
        {pulse ? (
          <span className={classNames('absolute inline-flex h-full w-full rounded-full opacity-75 beam-pulse', dotColors[tone])} />
        ) : null}
        <span className={classNames('relative inline-flex h-1.5 w-1.5 rounded-full', dotColors[tone])} />
      </span>
      <span className="text-[10px] font-medium uppercase tracking-[0.18em] text-dim">
        {label}
      </span>
    </span>
  )
}
