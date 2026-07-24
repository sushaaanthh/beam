import { useMemo, useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'

import { BrandMark } from '../components/BrandMark'
import { Button } from '../components/Button'
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
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-beam-950 dark:text-white">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(14,165,233,0.12),_transparent_25%),radial-gradient(circle_at_bottom_left,_rgba(99,102,241,0.14),_transparent_24%)]" />

      <header className="relative z-30 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-950/70">
        <div className="mx-auto flex w-full max-w-[1800px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => setMobileNavOpen((current) => !current)}
              className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-100 lg:hidden dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
              aria-label="Toggle navigation"
            >
              <span className="text-xl leading-none">☰</span>
            </button>

            <Link to="/dashboard" aria-label="B.E.A.M. dashboard">
              <BrandMark compact />
            </Link>
          </div>

          <div className="hidden max-w-2xl flex-1 items-center justify-center gap-3 text-sm text-slate-500 lg:flex dark:text-slate-400">
            <span className="rounded-full border border-slate-200 bg-white px-4 py-2 dark:border-slate-800 dark:bg-slate-900">
              Behavior-first analytics shell
            </span>
            <span className="rounded-full border border-slate-200 bg-white px-4 py-2 dark:border-slate-800 dark:bg-slate-900">
              Secure JWT session
            </span>
          </div>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <div className="hidden items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 lg:flex dark:border-slate-800 dark:bg-slate-900">
              <UserAvatar name={displayName} />
              <div className="min-w-0">
                <p className="text-sm font-semibold text-slate-900 dark:text-white">{displayName}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">Authenticated session</p>
              </div>
            </div>
            <Button variant="ghost" onClick={logout} className="hidden sm:inline-flex">
              Sign out
            </Button>
          </div>
        </div>
      </header>

      <div className="relative z-20 mx-auto flex w-full max-w-[1800px] gap-6 px-4 py-4 sm:px-6 lg:px-8">
        <aside
          className={classNames(
            'fixed inset-y-0 left-0 z-40 w-72 border-r border-slate-200 bg-white px-4 py-6 shadow-2xl shadow-slate-950/10 transition-transform duration-300 lg:static lg:z-auto lg:block lg:translate-x-0 lg:rounded-[2rem] lg:border dark:border-slate-800 dark:bg-slate-950/95',
            mobileNavOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          )}
        >
          <div className="flex h-full flex-col gap-6">
            <div className="lg:hidden">
              <BrandMark />
            </div>

            <nav className="space-y-2">
              {navigationItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileNavOpen(false)}
                  className={({ isActive }) =>
                    classNames(
                      'flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition',
                      isActive
                        ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-950'
                        : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900',
                    )
                  }
                >
                  <span>{item.label}</span>
                  <span className="text-xs opacity-60">→</span>
                </NavLink>
              ))}
            </nav>

            <div className="rounded-[1.5rem] border border-cyan-500/20 bg-cyan-500/10 p-5 text-sm text-slate-600 dark:text-slate-300">
              <p className="text-xs font-semibold tracking-[0.3em] text-cyan-600 uppercase dark:text-cyan-400">Session status</p>
              <p className="mt-3 leading-7">
                Your JWT session is active. The shell is ready for profile-aware analytics, history, and settings flows.
              </p>
            </div>
          </div>
        </aside>

        {mobileNavOpen ? (
          <button
            type="button"
            onClick={() => setMobileNavOpen(false)}
            className="fixed inset-0 z-30 bg-slate-950/50 lg:hidden"
            aria-label="Close navigation overlay"
          />
        ) : null}

        <main className="relative min-w-0 flex-1 space-y-6">
          <Outlet />

          <footer className="rounded-[1.5rem] border border-slate-200 bg-white px-5 py-4 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
            B.E.A.M. frontend shell • Responsive dashboard layout • React Router protected routes • TanStack Query data layer
          </footer>
        </main>
      </div>
    </div>
  )
}