import type { ReactNode } from 'react'

import { classNames } from '../utils/classNames'

type DialogProps = {
  open: boolean
  title: string
  description?: string
  children?: ReactNode
  actions?: ReactNode
  onClose?: () => void
  className?: string
}

export function Dialog({ open, title, description, children, actions, onClose, className }: DialogProps) {
  if (!open) {
    return null
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/72 p-4 backdrop-blur-xl"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        className={classNames(
          'w-full max-w-xl rounded-[1.5rem] border border-white/12 bg-[linear-gradient(180deg,rgba(20,20,20,0.96),rgba(12,12,12,0.98))] p-6 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_30px_80px_rgba(0,0,0,0.72)]',
          className,
        )}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
            {description ? <p className="text-sm leading-6 text-white/60">{description}</p> : null}
          </div>
          {onClose ? (
            <button
              type="button"
              onClick={onClose}
              className="inline-flex h-10 w-10 items-center justify-center rounded-[1rem] border border-white/10 bg-white/4 text-white/72 transition duration-200 hover:-translate-y-px hover:border-white/16 hover:bg-white/6 active:translate-y-px"
              aria-label="Close dialog"
            >
              ×
            </button>
          ) : null}
        </div>

        {children ? <div className="mt-6">{children}</div> : null}
        {actions ? <div className="mt-6 flex items-center justify-end gap-3">{actions}</div> : null}
      </div>
    </div>
  )
}