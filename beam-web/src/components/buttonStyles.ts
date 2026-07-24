import { classNames } from '../utils/classNames'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'border-white/12 bg-[linear-gradient(180deg,rgba(248,248,248,0.98),rgba(215,215,215,0.94))] text-[#050505] shadow-[inset_0_1px_0_rgba(255,255,255,0.42),0_14px_28px_rgba(0,0,0,0.42)] hover:-translate-y-px hover:border-white/18 hover:bg-[linear-gradient(180deg,rgba(252,252,252,1),rgba(225,225,225,0.96))] focus-visible:ring-white/30',
  secondary:
    'border-white/10 bg-white/4 text-white/88 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] hover:-translate-y-px hover:border-white/16 hover:bg-white/6 focus-visible:ring-white/20',
  ghost: 'border-transparent bg-transparent text-white/72 hover:bg-white/5 focus-visible:ring-white/20',
  danger: 'border-rose-400/20 bg-rose-400/12 text-rose-100 hover:-translate-y-px hover:bg-rose-400/18 focus-visible:ring-rose-300/30',
}

export function buttonClassName(variant: ButtonVariant = 'primary', className?: string) {
  return classNames(
    'inline-flex items-center justify-center gap-2 rounded-[1rem] border px-4 py-3 text-sm font-medium tracking-tight transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-55 active:translate-y-px',
    variantClasses[variant],
    className,
  )
}