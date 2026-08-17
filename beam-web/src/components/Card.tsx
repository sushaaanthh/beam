import type { HTMLAttributes, ReactNode, ForwardRefExoticComponent, RefAttributes } from 'react'

export type CardProps = HTMLAttributes<HTMLDivElement> & {
  variant?: 'default' | 'elevated' | 'glass' | 'outlined'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  children: ReactNode
}

const variantStyles = {
  default: `
    bg-[#101010] border border-[#222222] text-[#F5F5F0]
    shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_4px_16px_rgba(0,0,0,0.6)]
  `,
  elevated: `
    bg-[#141414] border border-[#282828] text-[#F5F5F0]
    shadow-[inset_0_1px_0_rgba(255,255,255,0.07),0_8px_24px_rgba(0,0,0,0.8)]
  `,
  glass: `
    bg-[#101010]/80 backdrop-blur-md border border-[#222222] text-[#F5F5F0]
    shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_4px_16px_rgba(0,0,0,0.6)]
  `,
  outlined: `
    bg-transparent border border-[#222222] text-[#F5F5F0]
  `,
}

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

const hoverStyles = {
  true: 'transition-all duration-150 ease-out hover:border-[#383838] hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_6px_20px_rgba(0,0,0,0.8)] hover:-translate-y-[1px]',
  false: 'transition-colors duration-150 ease-out',
}

export const Card = Object.assign(
  (
    {
      variant = 'default',
      padding = 'md',
      hover = false,
      children,
      className = '',
      ...props
    }: CardProps
  ) => {
    return (
      <div
        className={`
          rounded-[14px]
          ${variantStyles[variant]}
          ${paddingStyles[padding]}
          ${hoverStyles[hover ? 'true' : 'false']}
          ${className}
        `}
        {...props}
      >
        {children}
      </div>
    )
  },
  {
    Elevated: (props: CardProps) => <Card variant="elevated" {...props} />,
    Glass: (props: CardProps) => <Card variant="glass" {...props} />,
    Outlined: (props: CardProps) => <Card variant="outlined" {...props} />,
    Compact: (props: CardProps) => <Card padding="sm" {...props} />,
    Spacious: (props: CardProps) => <Card padding="lg" {...props} />,
    Interactive: (props: CardProps) => <Card hover {...props} />,
  }
) as ForwardRefExoticComponent<CardProps & RefAttributes<HTMLDivElement>> & {
  Elevated: ForwardRefExoticComponent<CardProps & RefAttributes<HTMLDivElement>>
  Glass: ForwardRefExoticComponent<CardProps & RefAttributes<HTMLDivElement>>
  Outlined: ForwardRefExoticComponent<CardProps & RefAttributes<HTMLDivElement>>
  Compact: ForwardRefExoticComponent<CardProps & RefAttributes<HTMLDivElement>>
  Spacious: ForwardRefExoticComponent<CardProps & RefAttributes<HTMLDivElement>>
  Interactive: ForwardRefExoticComponent<CardProps & RefAttributes<HTMLDivElement>>
}