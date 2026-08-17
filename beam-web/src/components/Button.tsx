import type { ButtonHTMLAttributes, ReactNode, ForwardRefExoticComponent, RefAttributes } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'glass'
  size?: 'sm' | 'md' | 'lg'
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  isLoading?: boolean
  fullWidth?: boolean
}

const variantStyles = {
  primary: `
    bg-apple-accent text-white
    hover:bg-apple-accentHover active:bg-apple-accentHover
    shadow-apple-md hover:shadow-accent-glow active:shadow-apple-sm
    border border-transparent
  `,
  secondary: `
    bg-apple-bgCard text-apple-textPrimary
    hover:bg-apple-bgCardHover active:bg-apple-bgCard
    border border-apple-border hover:border-apple-borderHover active:border-apple-border
    shadow-apple-sm hover:shadow-apple-md active:shadow-apple-sm
  `,
  ghost: `
    bg-transparent text-apple-textPrimary
    hover:bg-apple-glass active:bg-apple-glassStrong
    border border-transparent hover:border-apple-glassBorder active:border-apple-glassBorder
  `,
  danger: `
    bg-apple-danger text-white
    hover:bg-apple-danger/90 active:bg-apple-danger
    shadow-apple-md hover:shadow-[0_0_0_1px_rgba(255,69,58,0.3),0_0_24px_rgba(255,69,58,0.15)] active:shadow-apple-sm
    border border-transparent
  `,
  glass: `
    bg-apple-glass text-apple-textPrimary
    hover:bg-apple-glassStrong active:bg-apple-glass
    border border-apple-glassBorder hover:border-apple-glassBorderStrong active:border-apple-glassBorder
    backdrop-blur-apple backdrop-filter
    shadow-apple-sm hover:shadow-apple-md active:shadow-apple-sm
  `,
}

const sizeStyles = {
  sm: 'px-3 py-2 text-caption-lg gap-1.5',
  md: 'px-5 py-3 text-body-md gap-2',
  lg: 'px-7 py-4 text-body-lg gap-2.5',
}

const fullWidthStyles = {
  true: 'w-full justify-center',
  false: '',
}

export const Button = Object.assign(
  (
    {
      variant = 'primary',
      size = 'md',
      leftIcon,
      rightIcon,
      isLoading = false,
      fullWidth = false,
      children,
      className = '',
      disabled,
      type = 'button',
      ...props
    }: ButtonProps
  ) => {
    const isDisabled = disabled || isLoading

    return (
      <button
        type={type}
        className={`
          relative inline-flex items-center justify-center font-semibold tracking-tight
          rounded-apple-lg
          transition-all duration-apple-fast ease-apple
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-apple-accent focus-visible:ring-offset-2 focus-visible:ring-offset-apple-bg
          disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:transform-none disabled:active:transform-none
          active:scale-[0.98] active:transition-none
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${fullWidthStyles[fullWidth ? 'true' : 'false']}
          ${className}
        `}
        disabled={isDisabled}
        {...props}
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <svg
              className="h-4 w-4 animate-spin text-current"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="3"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </span>
        ) : leftIcon ? (
          <span className="flex items-center justify-center" aria-hidden="true">{leftIcon}</span>
        ) : null}
        <span className="relative z-10">{children}</span>
        {!isLoading && rightIcon && (
          <span className="flex items-center justify-center" aria-hidden="true">{rightIcon}</span>
        )}
      </button>
    )
  },
  {
    Primary: (props: ButtonProps) => <Button variant="primary" {...props} />,
    Secondary: (props: ButtonProps) => <Button variant="secondary" {...props} />,
    Ghost: (props: ButtonProps) => <Button variant="ghost" {...props} />,
    Danger: (props: ButtonProps) => <Button variant="danger" {...props} />,
    Glass: (props: ButtonProps) => <Button variant="glass" {...props} />,
    Small: (props: ButtonProps) => <Button size="sm" {...props} />,
    Large: (props: ButtonProps) => <Button size="lg" {...props} />,
    FullWidth: (props: ButtonProps) => <Button fullWidth {...props} />,
  }
) as ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>> & {
  Primary: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
  Secondary: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
  Ghost: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
  Danger: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
  Glass: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
  Small: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
  Large: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
  FullWidth: ForwardRefExoticComponent<ButtonProps & RefAttributes<HTMLButtonElement>>
}