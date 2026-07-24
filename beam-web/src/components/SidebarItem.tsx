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
          'group flex items-center justify-between rounded-[1rem] border px-4 py-3 text-sm font-medium tracking-tight transition duration-200 active:translate-y-px',
          isActive
            ? 'border-white/14 bg-white/8 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_12px_24px_rgba(0,0,0,0.28)]'
            : 'border-transparent bg-transparent text-white/68 hover:border-white/10 hover:bg-white/5 hover:text-white',
        )
      }
    >
      <span>{label}</span>
      <span className="text-[0.65rem] uppercase tracking-[0.3em] text-white/26 transition group-hover:text-white/46">key</span>
    </NavLink>
  )
}