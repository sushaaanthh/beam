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
        'flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-900 via-slate-700 to-cyan-500 text-sm font-semibold text-white dark:from-slate-100 dark:via-slate-200 dark:to-cyan-300 dark:text-slate-900',
        className,
      )}
      aria-label={name}
    >
      {initials || 'U'}
    </div>
  )
}