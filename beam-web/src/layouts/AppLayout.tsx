import { useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Brain,
  History,
  Database,
  Cpu,
  BarChart3,
  FileText,
  Settings,
  User,
  Plus,
  LogOut,
  Bell,
  Search,
  Menu,
  X,
} from 'lucide-react'

import { BrandMark } from '../components/BrandMark'
import { Button } from '../components/Button'
import { SidebarItem } from '../components/SidebarItem'
import { UserAvatar } from '../components/UserAvatar'
import { useAuth } from '../hooks/useAuth'

const mainNavItems = [
  { to: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
  { to: '/analysis', label: 'Analyze', icon: <Brain className="h-4 w-4" /> },
  { to: '/history', label: 'History', icon: <History className="h-4 w-4" /> },
  { to: '/datasets', label: 'Datasets', icon: <Database className="h-4 w-4" /> },
  { to: '/models', label: 'Models', icon: <Cpu className="h-4 w-4" /> },
  { to: '/insights', label: 'Insights', icon: <BarChart3 className="h-4 w-4" /> },
  { to: '/reports', label: 'Reports', icon: <FileText className="h-4 w-4" /> },
]

const secondaryNavItems = [
  { to: '/settings', label: 'Settings', icon: <Settings className="h-4 w-4" /> },
  { to: '/profile', label: 'Profile', icon: <User className="h-4 w-4" /> },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const location = useLocation()

  const displayName = user?.username ?? 'Researcher'

  return (
    <div className="min-h-screen bg-[#050505] text-[#F5F5F0] flex flex-col selection:bg-[#C7FF4A] selection:text-[#050505]">
      {/* Top Application Bar */}
      <header className="sticky top-0 z-40 border-b border-[#1C1C1C] bg-[#080808]/95 backdrop-blur-md px-4 sm:px-6 lg:px-8 py-2.5">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              className="lg:hidden flex h-8 w-8 items-center justify-center rounded-lg bg-[#141414] border border-[#262626] text-[#B8B8B0]"
              aria-label="Toggle navigation"
            >
              {mobileNavOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
            <BrandMark compact />
            <div className="hidden sm:block border-l border-[#262626] pl-3 py-0.5">
              <span className="text-[11px] font-mono tracking-widest text-[#73736F] uppercase">
                Instrument Workspace
              </span>
            </div>
          </div>

          {/* Header Search & Actions */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 bg-[#0E0E0E] border border-[#222222] rounded-lg px-3 py-1.5 text-xs text-[#73736F] w-64 shadow-[inset_0_1px_2px_rgba(0,0,0,0.5)]">
              <Search className="h-3.5 w-3.5 text-[#555552]" />
              <input
                type="text"
                placeholder="Search analyses, models, logs..."
                className="bg-transparent text-xs text-[#F5F5F0] placeholder:text-[#555552] focus:outline-none w-full"
              />
              <span className="font-mono text-[10px] bg-[#1A1A1A] border border-[#2A2A2A] rounded px-1.5 py-0.5 text-[#73736F]">
                ⌘K
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#141414] border border-[#262626] text-[#B8B8B0] hover:text-white transition-colors"
                title="Notifications"
                aria-label="Notifications"
              >
                <Bell className="h-3.5 w-3.5" />
              </button>

              <Link to="/analysis">
                <Button variant="primary" size="sm" leftIcon={<Plus className="h-3.5 w-3.5 stroke-[2.5]" />}>
                  New Analysis
                </Button>
              </Link>

              <div className="hidden sm:flex items-center gap-2.5 pl-2 border-l border-[#1C1C1C]">
                <UserAvatar name={displayName} size="sm" />
                <div className="min-w-0 hidden xl:block">
                  <p className="text-xs font-semibold text-[#F5F5F0] leading-none truncate">{displayName}</p>
                  <p className="text-[10px] text-[#73736F] font-mono mt-0.5">AUTH_READY</p>
                </div>
                <button
                  type="button"
                  onClick={logout}
                  className="flex h-7 w-7 items-center justify-center rounded-md text-[#73736F] hover:text-[#FF6B6B] hover:bg-[#1A0E0E] transition-colors ml-1"
                  title="Sign out"
                  aria-label="Sign out"
                >
                  <LogOut className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid: Sidebar + Workspace */}
      <div className="flex-1 flex max-w-[1920px] w-full mx-auto">
        {/* Persistent Left Sidebar */}
        <aside
          className={`
            fixed inset-y-0 left-0 z-30 w-64 bg-[#080808] border-r border-[#1C1C1C] px-3 py-4 flex flex-col justify-between
            transition-transform duration-200 lg:static lg:translate-x-0 top-[53px] lg:top-0 h-[calc(100vh-53px)] lg:h-auto
            ${mobileNavOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          `}
        >
          <div className="space-y-6">
            <div>
              <p className="px-3 text-[10px] font-semibold tracking-[0.16em] text-[#555552] uppercase mb-2">
                Core Engine
              </p>
              <nav className="space-y-1">
                {mainNavItems.map((item) => (
                  <SidebarItem
                    key={item.to}
                    to={item.to}
                    label={item.label}
                    icon={item.icon}
                    onClick={() => setMobileNavOpen(false)}
                  />
                ))}
              </nav>
            </div>

            <div className="pt-3 border-t border-[#181818]">
              <p className="px-3 text-[10px] font-semibold tracking-[0.16em] text-[#555552] uppercase mb-2">
                Preferences
              </p>
              <nav className="space-y-1">
                {secondaryNavItems.map((item) => (
                  <SidebarItem
                    key={item.to}
                    to={item.to}
                    label={item.label}
                    icon={item.icon}
                    onClick={() => setMobileNavOpen(false)}
                  />
                ))}
              </nav>
            </div>
          </div>

          {/* System Status Keycap Module at Sidebar Bottom */}
          <div className="mt-auto pt-4 border-t border-[#181818]">
            <div className="rounded-lg bg-[#0E0E0E] border border-[#1E1E1E] p-3 shadow-[inset_0_1px_2px_rgba(0,0,0,0.6)]">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-[#73736F] uppercase">System Status</span>
                <span className="inline-flex items-center gap-1.5 text-[11px] font-mono text-[#C7FF4A]">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A] shadow-[0_0_4px_#C7FF4A]"></span>
                  ONLINE
                </span>
              </div>
              <div className="mt-2.5 flex items-center justify-between text-xs text-[#B8B8B0] pt-2 border-t border-[#181818]">
                <span className="text-[11px] text-[#73736F]">Active Model</span>
                <span className="font-mono text-[11px] font-semibold text-[#F5F5F0]">RoBERTa-v1.2</span>
              </div>
            </div>
          </div>
        </aside>

        {mobileNavOpen && (
          <button
            type="button"
            onClick={() => setMobileNavOpen(false)}
            className="fixed inset-0 z-20 bg-black/70 lg:hidden"
            aria-label="Close navigation overlay"
          />
        )}

        {/* Right Application Workspace */}
        <main className="flex-1 min-w-0 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
