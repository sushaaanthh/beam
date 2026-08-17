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

export function NavigationBar({ brand, items, actions, onMenuToggle, menuOpen, className = '' }: NavigationBarProps) {
  return (
    <header
      className={classNames(
        'sticky top-0 z-40 border-b border-[#1C1C1C] bg-[#050505]/90 backdrop-blur-md',
        className,
      )}
    >
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          {onMenuToggle ? (
            <button
              type="button"
              onClick={onMenuToggle}
              className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#141414] border border-[#262626] text-[#B8B8B0] hover:text-white lg:hidden"
              aria-label="Toggle navigation"
              aria-expanded={menuOpen}
            >
              {menuOpen ? (
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 12h18M3 6h18M3 18h18" />
                </svg>
              )}
            </button>
          ) : null}

          {brand}
        </div>

        {items?.length ? (
          <nav className="hidden items-center gap-1 lg:flex bg-[#0D0D0D] p-1 rounded-lg border border-[#1E1E1E]">
            {items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  classNames(
                    'px-3.5 py-1.5 rounded-md text-xs font-medium transition-all duration-150',
                    isActive
                      ? 'bg-[#181818] text-[#F5F5F0] border border-[#2E2E2E] shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]'
                      : 'text-[#B8B8B0] hover:text-white hover:bg-[#141414]',
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