import { classNames } from '../utils/classNames'

type UserAvatarProps = {
  name: string
  className?: string
}

export function UserAvatar({ name, className }: UserAvatarProps) {
  const initials = name
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <div
      className={classNames(
        'flex h-11 w-11 items-center justify-center rounded-[1rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] text-sm font-semibold text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]',
        className,
      )}
      aria-label={name}
    >
      {initials || 'U'}
    </div>
  )
}