import type { HTMLAttributes, ReactNode, ForwardRefExoticComponent, RefAttributes } from 'react'

type CardProps = HTMLAttributes<HTMLDivElement> & {
  variant?: 'default' | 'elevated' | 'glass' | 'outlined'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  children: ReactNode
}

const variantStyles = {
  default: `
    bg-apple-bgCard border border-apple-border
    hover:border-apple-borderHover hover:bg-apple-bgCardHover
  `,
  elevated: `
    bg-apple-bgCard border border-apple-border
    shadow-apple-lg hover:shadow-apple-xl
  `,
  glass: `
    bg-apple-glass border border-apple-glassBorder
    backdrop-blur-apple backdrop-filter
    hover:bg-apple-glassStrong hover:border-apple-glassBorderStrong
    shadow-apple-glow
  `,
  outlined: `
    bg-transparent border border-apple-border
    hover:border-apple-borderHover hover:bg-apple-glass
  `,
}

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

const hoverStyles = {
  true: `
    transition-all duration-apple-normal ease-apple
    hover:-translate-y-1 hover:shadow-apple-lg
    active:translate-y-0 active:shadow-apple-md active:transition-none
  `,
  false: 'transition-colors duration-apple-fast ease-apple',
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
          rounded-apple-xl
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