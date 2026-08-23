import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { classNames } from '../../utils/classNames'

type KeycapIconButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  /** Required for accessibility — icon-only buttons must be labelled. */
  'aria-label': string
  size?: 'sm' | 'md'
  children: ReactNode
}

const sizeClasses = {
  sm: 'h-8 w-8',
  md: 'h-10 w-10',
}

export function KeycapIconButton({
  size = 'md',
  children,
  className,
  type = 'button',
  ...props
}: KeycapIconButtonProps) {
  return (
    <button
      type={type}
      className={classNames('kc', sizeClasses[size], className)}
      {...props}
    >
      <span className="inline-flex items-center justify-center" aria-hidden="true">
        {children}
      </span>
    </button>
  )
}
