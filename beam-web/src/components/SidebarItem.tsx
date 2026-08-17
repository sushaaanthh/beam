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
          'group flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium border transition-all duration-150 ease-out select-none',
          isActive
            ? 'bg-[#161616] border-[#2E2E2E] text-[#F5F5F0] shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_2px_4px_rgba(0,0,0,0.5)] translate-y-[1px]'
            : 'border-transparent text-[#B8B8B0] hover:bg-[#121212] hover:border-[#222222] hover:text-[#F5F5F0] hover:-translate-y-[1px]'
        )
      }
    >
      {({ isActive }) => (
        <>
          {icon && (
            <span
              className={classNames(
                'flex h-4 w-4 shrink-0 items-center justify-center transition-colors',
                isActive ? 'text-[#C7FF4A]' : 'text-[#73736F] group-hover:text-[#B8B8B0]'
              )}
              aria-hidden="true"
            >
              {icon}
            </span>
          )}
          <span className="truncate">{label}</span>
          {isActive && (
            <span className="ml-auto flex h-1.5 w-1.5 rounded-full bg-[#C7FF4A] shadow-[0_0_6px_#C7FF4A]" aria-hidden="true" />
          )}
        </>
      )}
    </NavLink>
  )
}