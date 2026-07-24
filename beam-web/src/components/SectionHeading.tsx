import type { ReactNode } from 'react'

import { classNames } from '../utils/classNames'

type SectionHeadingProps = {
  eyebrow?: string
  title: string
  description?: string
  actions?: ReactNode
  className?: string
}

export function SectionHeading({ eyebrow, title, description, actions, className }: SectionHeadingProps) {
  return (
    <div className={classNames('flex flex-col gap-4 md:flex-row md:items-end md:justify-between', className)}>
      <div className="max-w-3xl space-y-3">
        {eyebrow ? <p className="text-xs font-semibold tracking-[0.32em] text-cyan-600 uppercase dark:text-cyan-400">{eyebrow}</p> : null}
        <h2 className="text-2xl font-semibold tracking-tight text-slate-950 dark:text-white md:text-3xl">{title}</h2>
        {description ? <p className="text-sm leading-7 text-slate-600 dark:text-slate-300 md:text-base">{description}</p> : null}
      </div>
      {actions ? <div className="flex shrink-0 items-center gap-3">{actions}</div> : null}
    </div>
  )
}