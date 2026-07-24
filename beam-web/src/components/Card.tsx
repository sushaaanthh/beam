import type { HTMLAttributes } from 'react'

import { classNames } from '../utils/classNames'

type CardProps = HTMLAttributes<HTMLDivElement>

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={classNames(
        'rounded-[1.5rem] border border-white/8 bg-white/75 p-6 shadow-glow backdrop-blur-xl dark:border-white/10 dark:bg-slate-900/70',
        className,
      )}
      {...props}
    />
  )
}