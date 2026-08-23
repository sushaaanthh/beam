import type { ReactNode } from 'react'
import { classNames } from '../../utils/classNames'

type SectionHeadingProps = {
  eyebrow?: string
  title: string
  description?: string
  actions?: ReactNode
  align?: 'start' | 'center'
  className?: string
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  actions,
  align = 'start',
  className,
}: SectionHeadingProps) {
  return (
    <div
      className={classNames(
        'flex flex-col gap-5 border-b border-line-subtle pb-6 md:flex-row md:items-end md:justify-between',
        className,
      )}
    >
      <div className={classNames('max-w-3xl space-y-3', align === 'center' && 'md:mx-auto md:text-center')}>
        {eyebrow ? (
          <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-lime">
            {eyebrow}
          </p>
        ) : null}
        <h2 className="font-display text-3xl font-semibold leading-tight text-chalk sm:text-4xl">
          {title}
        </h2>
        {description ? (
          <p className="text-sm leading-relaxed text-mist">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex shrink-0 items-center gap-3">{actions}</div> : null}
    </div>
  )
}
