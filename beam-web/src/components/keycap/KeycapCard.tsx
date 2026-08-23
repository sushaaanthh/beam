import type { HTMLAttributes } from 'react'
import { classNames } from '../../utils/classNames'

type KeycapCardProps = HTMLAttributes<HTMLDivElement> & {
  /** Adds restrained tactile hover lift. Only for non-interactive framing. */
  interactive?: boolean
}

export function KeycapCard({ interactive = false, className, children, ...props }: KeycapCardProps) {
  return (
    <div
      className={classNames('kc-card', interactive && 'kc-card--interactive', className)}
      {...props}
    >
      {children}
    </div>
  )
}
