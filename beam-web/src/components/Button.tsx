import type { ButtonHTMLAttributes, ReactNode, ForwardRefExoticComponent, RefAttributes } from 'react'

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'icon' | 'glass'
  size?: 'sm' | 'md' | 'lg'
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  isLoading?: boolean
  fullWidth?: boolean
}

const variantStyles = {
  primary: `
    bg-[#C7FF4A] text-[#050505] font-semibold border border-[#A8D83A]
    shadow-[inset_0_1px_0_rgba(255,255,255,0.45),inset_0_-1px_0_rgba(0,0,0,0.25),0_2px_6px_rgba(199,255,74,0.2)]
    hover:bg-[#D4FF6A] hover:border-[#C7FF4A] hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.5),0_4px_12px_rgba(199,255,74,0.3)]
    active:bg-[#A8D83A] active:shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]
  `,
  secondary: `
    bg-[#161616] text-[#F5F5F0] font-medium border border-[#262626]
    shadow-[inset_0_1px_0_rgba(255,255,255,0.08),inset_0_-1px_0_rgba(0,0,0,0.5),0_2px_4px_rgba(0,0,0,0.6)]
    hover:border-[#383838] hover:text-white hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_4px_8px_rgba(0,0,0,0.8)]
    active:bg-[#111111] active:border-[#1E1E1E] active:shadow-[inset_0_2px_4px_rgba(0,0,0,0.8)]
  `,
  ghost: `
    bg-transparent text-[#B8B8B0] font-medium border border-transparent
    hover:bg-[#121212] hover:border-[#262626] hover:text-[#F5F5F0] hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_2px_4px_rgba(0,0,0,0.4)]
    active:bg-[#0D0D0D] active:shadow-[inset_0_2px_3px_rgba(0,0,0,0.6)]
  `,
  danger: `
    bg-[#180E0E] text-[#FF6B6B] font-medium border border-[#3E1C1C]
    shadow-[inset_0_1px_0_rgba(255,107,107,0.15),inset_0_-1px_0_rgba(0,0,0,0.5),0_2px_4px_rgba(0,0,0,0.6)]
    hover:bg-[#221313] hover:border-[#5A2525] hover:text-[#FF8888]
    active:bg-[#140A0A] active:shadow-[inset_0_2px_4px_rgba(0,0,0,0.8)]
  `,
  icon: `
    bg-[#161616] text-[#B8B8B0] border border-[#262626]
    shadow-[inset_0_1px_0_rgba(255,255,255,0.08),inset_0_-1px_0_rgba(0,0,0,0.5),0_2px_4px_rgba(0,0,0,0.6)]
    hover:border-[#383838] hover:text-[#F5F5F0]
    active:bg-[#111111] active:shadow-[inset_0_2px_4px_rgba(0,0,0,0.8)]
  `,
  glass: `
    bg-[#121212]/80 backdrop-blur-md text-[#F5F5F0] font-medium border border-[#262626]
    shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_2px_6px_rgba(0,0,0,0.5)]
    hover:border-[#383838] hover:bg-[#161616]
    active:bg-[#0E0E0E]
  `,
}

const sizeStyles = {
  sm: 'px-3 py-1.5 text-xs rounded-md gap-1.5',
  md: 'px-4 py-2 text-sm rounded-lg gap-2',
  lg: 'px-5 py-2.5 text-base rounded-lg gap-2.5',
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
        disabled={isDisabled}
        className={`
          relative inline-flex items-center justify-center font-ui tracking-tight select-none cursor-pointer
          transition-all duration-150 ease-out
          hover:-translate-y-[1px]
          active:translate-y-[1px]
          disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C7FF4A] focus-visible:ring-offset-2 focus-visible:ring-offset-[#050505]
          ${variantStyles[variant] || variantStyles.secondary}
          ${sizeStyles[size]}
          ${fullWidth ? 'w-full' : ''}
          ${className}
        `}
        {...props}
      >
        {isLoading ? (
          <span className="flex items-center justify-center mr-1">
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
          <span className="flex items-center justify-center shrink-0" aria-hidden="true">{leftIcon}</span>
        ) : null}
        <span>{children}</span>
        {!isLoading && rightIcon && (
          <span className="flex items-center justify-center shrink-0" aria-hidden="true">{rightIcon}</span>
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