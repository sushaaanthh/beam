import { NavLink } from 'react-router-dom'

import { classNames } from '../utils/classNames'

type SidebarItemProps = {
  to: string
  label: string
  onClick?: () => void
}

export function SidebarItem({ to, label, onClick }: SidebarItemProps) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        classNames(
          'kds-keycap-interactive group flex items-center justify-between rounded-[14px] border px-4 py-3 text-sm font-medium tracking-tight',
          isActive
            ? 'kds-inset border-[#b2ff7d]/35 text-white'
            : 'border-transparent bg-transparent text-white/68 hover:border-white/10 hover:bg-white/5 hover:text-white',
        )
      }
    >
      <span>{label}</span>
      <span className="text-[0.65rem] uppercase tracking-[0.3em] text-white/26 transition group-hover:text-[#b2ff7d]">key</span>
    </NavLink>
  )
}
