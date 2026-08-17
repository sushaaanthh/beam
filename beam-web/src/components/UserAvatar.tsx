import type { HTMLAttributes } from 'react'

type UserAvatarProps = HTMLAttributes<HTMLDivElement> & {
  name: string
  src?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const sizeStyles = {
  sm: 'h-8 w-8 text-caption-lg',
  md: 'h-10 w-10 text-body-sm',
  lg: 'h-12 w-12 text-body-md',
  xl: 'h-16 w-16 text-heading-lg',
}

const gradientStyles = [
  'from-apple-accent to-apple-accent/70',
  'from-apple-success to-apple-success/70',
  'from-apple-warning to-apple-warning/70',
  'from-purple-500 to-purple-500/70',
  'from-pink-500 to-pink-500/70',
  'from-orange-500 to-orange-500/70',
  'from-cyan-500 to-cyan-500/70',
  'from-indigo-500 to-indigo-500/70',
]

function getGradientForName(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return gradientStyles[Math.abs(hash) % gradientStyles.length]
}

export function UserAvatar({ name, src, size = 'md', className, ...props }: UserAvatarProps) {
  const initials = name
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  const gradient = getGradientForName(name)

  return (
    <div
      className={`relative flex items-center justify-center rounded-apple-full bg-gradient-to-br ${gradient} text-white font-semibold shadow-apple-sm ${sizeStyles[size]} ${className}`}
      aria-label={name}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt=""
          className="h-full w-full rounded-apple-full object-cover"
        />
      ) : (
        initials || 'U'
      )}
      <span className="absolute -bottom-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-apple-bg border-2 border-apple-bg" aria-hidden="true">
        <span className="h-1.5 w-1.5 rounded-full bg-apple-success" />
      </span>
    </div>
  )
}