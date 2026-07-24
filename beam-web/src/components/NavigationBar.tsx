import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

import { classNames } from '../utils/classNames'

export type NavigationBarItem = {
  to: string
  label: string
}

type NavigationBarProps = {
  brand: ReactNode
  items?: NavigationBarItem[]
  actions?: ReactNode
  onMenuToggle?: () => void
  menuOpen?: boolean
  className?: string
}

export function NavigationBar({ brand, items, actions, onMenuToggle, menuOpen, className }: NavigationBarProps) {
  return (
    <header
      className={classNames(
        'relative z-30 border-b border-white/10 bg-[#080808] shadow-[inset_0_-1px_0_rgba(255,255,255,0.04)]',
        className,
      )}
    >
      <div className="mx-auto flex w-full max-w-[1800px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          {onMenuToggle ? (
            <button
              type="button"
              onClick={onMenuToggle}
              className="kds-keycap kds-keycap-interactive inline-flex h-11 w-11 items-center justify-center rounded-[14px] text-white/78 lg:hidden"
              aria-label="Toggle navigation"
              aria-expanded={menuOpen}
            >
              <span className="text-xl leading-none" aria-hidden="true">
                {menuOpen ? '×' : '☰'}
              </span>
            </button>
          ) : null}

          {brand}
        </div>

        {items?.length ? (
          <nav className="hidden items-center gap-2 lg:flex">
            {items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  classNames(
                    'kds-keycap-interactive rounded-[14px] border px-4 py-3 text-sm font-medium tracking-tight',
                    isActive
                      ? 'kds-inset border-[#b2ff7d]/35 text-white'
                      : 'border-transparent text-white/68 hover:border-white/10 hover:bg-white/5 hover:text-white',
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        ) : (
          <div className="hidden lg:block" />
        )}

        <div className="flex items-center gap-3">{actions}</div>
      </div>
    </header>
  )
}
