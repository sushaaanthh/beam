import { classNames } from '../utils/classNames'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'border-[#b2ff7d]/45 bg-[#b2ff7d] text-[#081004] shadow-[inset_0_1px_0_rgba(255,255,255,0.5),inset_0_-1px_0_rgba(0,0,0,0.22),0_2px_0_#497b2e,0_10px_20px_rgba(0,0,0,0.35)] hover:border-[#d1ffb3] hover:bg-[#c1ff99] focus-visible:ring-[#b2ff7d]/40',
  secondary:
    'kds-keycap border-white/12 text-white/88 hover:border-white/22 focus-visible:ring-white/20',
  ghost: 'border-white/8 bg-transparent text-white/62 hover:border-white/16 hover:bg-white/5 focus-visible:ring-white/20',
  danger: 'border-rose-400/20 bg-rose-400/12 text-rose-100 hover:-translate-y-px hover:bg-rose-400/18 focus-visible:ring-rose-300/30',
}

export function buttonClassName(variant: ButtonVariant = 'primary', className?: string) {
  return classNames(
    'kds-keycap-interactive inline-flex items-center justify-center gap-2 rounded-[14px] border px-4 py-3 text-sm font-medium tracking-tight focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-55',
    variantClasses[variant],
    className,
  )
}
