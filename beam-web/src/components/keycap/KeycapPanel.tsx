import type { HTMLAttributes, ReactNode } from 'react'
import { classNames } from '../../utils/classNames'

type KeycapPanelProps = HTMLAttributes<HTMLElement> & {
  eyebrow?: string
  title?: string
  meta?: ReactNode
  bodyClassName?: string
  headerClassName?: string
}

export function KeycapPanel({
  eyebrow,
  title,
  meta,
  children,
  className,
  bodyClassName,
  headerClassName,
  ...props
}: KeycapPanelProps) {
  const hasHeader = Boolean(eyebrow || title || meta)

  return (
    <section className={classNames('kc-panel', className)} {...props}>
      {hasHeader ? (
        <header
          className={classNames(
            'flex flex-wrap items-center justify-between gap-3 border-b border-line-subtle px-5 py-4 sm:px-6',
            headerClassName,
          )}
        >
          <div className="flex items-baseline gap-3">
            {eyebrow ? (
              <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-dim">
                {eyebrow}
              </span>
            ) : null}
            {title ? (
              <h3 className="font-display text-sm font-medium uppercase tracking-[0.1em] text-chalk">
                {title}
              </h3>
            ) : null}
          </div>
          {meta ? <div className="flex items-center gap-3">{meta}</div> : null}
        </header>
      ) : null}
      <div className={classNames('p-5 sm:p-6', bodyClassName)}>{children}</div>
    </section>
  )
}
