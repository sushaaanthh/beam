import type { HTMLAttributes } from 'react'

type UserAvatarProps = HTMLAttributes<HTMLDivElement> & {
  name: string
  src?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const sizeStyles = {
  sm: 'h-7 w-7 text-[10px]',
  md: 'h-9 w-9 text-xs',
  lg: 'h-11 w-11 text-sm',
  xl: 'h-14 w-14 text-base',
}

export function UserAvatar({ name, src, size = 'md', className = '', ...props }: UserAvatarProps) {
  const initials = name
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <div
      className={`relative flex items-center justify-center rounded-lg bg-[#181818] border border-[#2A2A2A] text-[#F5F5F0] font-display tracking-wider font-semibold shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_2px_4px_rgba(0,0,0,0.5)] ${sizeStyles[size]} ${className}`}
      aria-label={name}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt=""
          className="h-full w-full rounded-lg object-cover"
        />
      ) : (
        initials || 'U'
      )}
      <span className="absolute -bottom-0.5 -right-0.5 flex h-2 w-2 items-center justify-center" aria-hidden="true">
        <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A] shadow-[0_0_4px_#C7FF4A]" />
      </span>
    </div>
  )
}