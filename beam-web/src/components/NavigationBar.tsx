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
        'relative z-30 border-b border-apple-border bg-apple-bg/80 backdrop-blur-apple-strong shadow-apple-inner',
        className,
      )}
    >
      <div className="mx-auto flex w-full max-w-[1800px] items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          {onMenuToggle ? (
            <button
              type="button"
              onClick={onMenuToggle}
              className="btn-icon-ghost rounded-apple-lg p-2.5 lg:hidden"
              aria-label="Toggle navigation"
              aria-expanded={menuOpen}
            >
              <span className="text-xl leading-none" aria-hidden="true">
                {menuOpen ? (
                  <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 12h18M3 6h18M3 18h18" />
                  </svg>
                )}
              </span>
            </button>
          ) : null}

          {brand}
        </div>

        {items?.length ? (
          <nav className="hidden items-center gap-1 lg:flex">
            {items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  classNames(
                    'nav-link',
                    isActive && 'nav-link-active',
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

        <div className="flex items-center gap-2">{actions}</div>
      </div>
    </header>
  )
}