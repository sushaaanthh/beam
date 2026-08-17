import { NavLink } from 'react-router-dom'

import { classNames } from '../utils/classNames'

type SidebarItemProps = {
  to: string
  label: string
  icon?: React.ReactNode
  onClick?: () => void
}

export function SidebarItem({ to, label, icon, onClick }: SidebarItemProps) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        classNames(
          'sidebar-item group flex items-center gap-3 rounded-apple-md px-3 py-2.5 text-body-md font-medium',
          isActive ? 'sidebar-item-active' : '',
        )
      }
    >
      {icon && (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center text-apple-textTertiary group-hover:text-apple-textPrimary transition-colors" aria-hidden="true">
          {icon}
        </span>
      )}
      <span className="truncate">{label}</span>
      {isActive && (
        <span className="ml-auto flex h-5 w-5 items-center justify-center rounded-apple-sm bg-apple-accentSoft text-apple-accent" aria-hidden="true">
          <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        </span>
      )}
    </NavLink>
  )
}