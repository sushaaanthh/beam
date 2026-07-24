import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  isLoading?: boolean
}

import { buttonClassName } from './buttonStyles'

export function Button({
  variant = 'primary',
  leftIcon,
  rightIcon,
  isLoading = false,
  children,
  className,
  disabled,
  type = 'button',
  ...buttonProps
}: ButtonProps) {
  return (
    <button
      type={type}
      className={buttonClassName(variant, className)}
      disabled={disabled || isLoading}
      {...buttonProps}
    >
      {isLoading ? (
        <span
          className={
            variant === 'primary'
              ? 'h-4 w-4 animate-spin rounded-full border-2 border-black/20 border-t-black'
              : 'h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white'
          }
        />
      ) : leftIcon}
      <span>{children}</span>
      {!isLoading ? rightIcon : null}
    </button>
  )
}

export function PrimaryButton(props: ButtonProps) {
  return <Button variant="primary" {...props} />
}

export function SecondaryButton(props: ButtonProps) {
  return <Button variant="secondary" {...props} />
}