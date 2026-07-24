import { classNames } from '../utils/classNames'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-sky-500 text-white shadow-lg shadow-sky-500/25 hover:bg-sky-400 focus-visible:ring-sky-400',
  secondary: 'bg-slate-800 text-slate-100 hover:bg-slate-700 focus-visible:ring-slate-400 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white',
  ghost: 'bg-transparent text-slate-700 hover:bg-slate-100 focus-visible:ring-slate-300 dark:text-slate-200 dark:hover:bg-slate-800',
  danger: 'bg-rose-500 text-white hover:bg-rose-400 focus-visible:ring-rose-400',
}

export function buttonClassName(variant: ButtonVariant = 'primary', className?: string) {
  return classNames(
    'inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-2.5 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-white disabled:cursor-not-allowed disabled:opacity-60 dark:focus-visible:ring-offset-slate-950',
    variantClasses[variant],
    className,
  )
}