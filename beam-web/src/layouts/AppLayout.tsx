import { useMemo, useState } from 'react'
import { Link, Outlet } from 'react-router-dom'

import { BrandMark } from '../components/BrandMark'
import { Button } from '../components/Button'
import { NavigationBar } from '../components/NavigationBar'
import { SidebarItem } from '../components/SidebarItem'
import { ThemeToggle } from '../components/ThemeToggle'
import { UserAvatar } from '../components/UserAvatar'
import { useAuth } from '../hooks/useAuth'
import { classNames } from '../utils/classNames'

const navigationItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/analysis', label: 'Analysis' },
  { to: '/history', label: 'History' },
  { to: '/profile', label: 'Profile' },
  { to: '/settings', label: 'Settings' },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const displayName = useMemo(() => user?.username ?? 'Researcher', [user?.username])

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.06),_transparent_22%),radial-gradient(circle_at_bottom_left,_rgba(166,177,255,0.08),_transparent_24%)]" />

      <NavigationBar
        brand={(
          <Link to="/dashboard" aria-label="B.E.A.M. dashboard">
            <BrandMark compact />
          </Link>
        )}
        onMenuToggle={() => setMobileNavOpen((current) => !current)}
        menuOpen={mobileNavOpen}
        actions={(
          <>
            <ThemeToggle />
            <div className="hidden items-center gap-3 rounded-[1rem] border border-white/10 bg-white/4 px-3 py-2 lg:flex">
              <UserAvatar name={displayName} />
              <div className="min-w-0">
                <p className="text-sm font-semibold text-white">{displayName}</p>
                <p className="text-xs text-white/48">Authenticated session</p>
              </div>
            </div>
            <Button variant="ghost" onClick={logout} className="hidden sm:inline-flex">
              Sign out
            </Button>
          </>
        )}
      />

      <div className="relative z-20 mx-auto flex w-full max-w-[1800px] gap-6 px-4 py-4 sm:px-6 lg:px-8">
        <aside
          className={classNames(
            'fixed inset-y-0 left-0 z-40 w-72 border-r border-white/8 bg-[#070707] px-4 py-6 transition-transform duration-300 lg:static lg:z-auto lg:block lg:translate-x-0 lg:rounded-[1.5rem] lg:border',
            mobileNavOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          )}
        >
          <div className="flex h-full flex-col gap-6">
            <div className="lg:hidden">
              <BrandMark />
            </div>

            <nav className="space-y-2">
              {navigationItems.map((item) => (
                <SidebarItem
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileNavOpen(false)}
                  label={item.label}
                />
              ))}
            </nav>

            <div className="rounded-[1.25rem] border border-white/10 bg-white/4 p-5 text-sm text-white/64">
              <p className="text-[0.7rem] font-semibold tracking-[0.34em] text-white/42 uppercase">Session status</p>
              <p className="mt-3 leading-7">
                Your JWT session is active. The shell is ready for analysis, history, profile, and settings flows.
              </p>
            </div>
          </div>
        </aside>

        {mobileNavOpen ? (
          <button
            type="button"
            onClick={() => setMobileNavOpen(false)}
            className="fixed inset-0 z-30 bg-black/65 lg:hidden"
            aria-label="Close navigation overlay"
          />
        ) : null}

        <main className="relative min-w-0 flex-1 space-y-6">
          <Outlet />

          <footer className="rounded-[1.25rem] border border-white/8 bg-white/4 px-5 py-4 text-sm text-white/56">
            B.E.A.M. frontend shell • Responsive dashboard layout • React Router protected routes • TanStack Query data layer
          </footer>
        </main>
      </div>
    </div>
  )
}