import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { classNames } from '../../utils/classNames'

export type KeycapVariant = 'primary' | 'graphite' | 'ghost'
export type KeycapSize = 'sm' | 'md' | 'lg'

const variantClasses: Record<KeycapVariant, string> = {
  primary: 'kc--primary',
  graphite: '',
  ghost: 'kc--ghost',
}

export const keycapSizeClasses: Record<KeycapSize, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-sm tracking-[0.08em]',
}

/**
 * Shared class string so anchors/links can render as keycaps too
 * (an <a> must never wrap a <button>).
 */
export function keycapClass(
  variant: KeycapVariant = 'graphite',
  size: KeycapSize = 'md',
  extra?: string,
): string {
  return classNames(
    'kc font-ui font-medium uppercase tracking-[0.06em]',
    variantClasses[variant],
    keycapSizeClasses[size],
    extra,
  )
}

type KeycapButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: KeycapVariant
  size?: KeycapSize
  fullWidth?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export function KeycapButton({
  variant = 'graphite',
  size = 'md',
  fullWidth = false,
  leftIcon,
  rightIcon,
  children,
  className,
  type = 'button',
  ...props
}: KeycapButtonProps) {
  return (
    <button
      type={type}
      className={keycapClass(variant, size, classNames(fullWidth && 'w-full', className))}
      {...props}
    >
      {leftIcon ? (
        <span className="inline-flex shrink-0 items-center" aria-hidden="true">{leftIcon}</span>
      ) : null}
      <span>{children}</span>
      {rightIcon ? (
        <span className="inline-flex shrink-0 items-center" aria-hidden="true">{rightIcon}</span>
      ) : null}
    </button>
  )
}
