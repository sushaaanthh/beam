import type { HTMLAttributes } from 'react'
import { classNames } from '../../utils/classNames'

type KeycapBadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: 'graphite' | 'lime' | 'outline'
}

const toneClasses = {
  graphite: 'bg-raised border-line-subtle text-mist',
  lime: 'bg-[rgba(199,255,74,0.05)] border-[rgba(199,255,74,0.25)] text-lime',
  outline: 'bg-transparent border-line-subtle text-dim',
}

export function KeycapBadge({ tone = 'graphite', className, children, ...props }: KeycapBadgeProps) {
  return (
    <span
      className={classNames(
        'inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1',
        'text-[10px] font-medium uppercase tracking-[0.14em]',
        toneClasses[tone],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  )
}
