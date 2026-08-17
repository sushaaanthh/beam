import type { ReactNode } from 'react'
import { X } from 'lucide-react'
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

export function Dialog({ open, title, description, children, actions, onClose, className = '' }: DialogProps) {
  if (!open) {
    return null
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        className={classNames(
          'w-full max-w-xl rounded-2xl border border-[#2A2A2A] bg-[#0E0E0E] p-6 text-[#F5F5F0] shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_30px_80px_rgba(0,0,0,0.85)]',
          className,
        )}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-[#1C1C1C] pb-3">
          <div className="space-y-1">
            <h2 className="font-display text-xl font-bold tracking-tight text-[#F5F5F0]">{title}</h2>
            {description ? <p className="text-xs text-[#73736F]">{description}</p> : null}
          </div>
          {onClose ? (
            <button
              type="button"
              onClick={onClose}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-[#73736F] hover:text-[#F5F5F0] hover:bg-[#1A1A1A]"
              aria-label="Close dialog"
            >
              <X className="h-4 w-4" />
            </button>
          ) : null}
        </div>

        {children ? <div className="mt-5">{children}</div> : null}
        {actions ? <div className="mt-6 flex items-center justify-end gap-3 pt-3 border-t border-[#1C1C1C]">{actions}</div> : null}
      </div>
    </div>
  )
}
