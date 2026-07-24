import { Link, NavLink, Outlet } from 'react-router-dom'

import { BrandMark } from '../components/BrandMark'
import { ThemeToggle } from '../components/ThemeToggle'
import { buttonClassName } from '../components/Button'
import { classNames } from '../utils/classNames'

const publicNavItems = [
  { to: '/', label: 'Home' },
  { to: '/login', label: 'Login' },
  { to: '/register', label: 'Register' },
]

export function PublicLayout() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-50 text-slate-950 dark:bg-beam-950 dark:text-white">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(99,102,241,0.18),_transparent_28%),linear-gradient(180deg,rgba(255,255,255,0.9),rgba(248,250,252,0.96))] dark:bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.16),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(99,102,241,0.16),_transparent_28%),linear-gradient(180deg,rgba(6,11,22,0.96),rgba(11,18,32,0.98))]" />
      <header className="relative z-10 border-b border-slate-200/70 bg-white/70 backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-950/50">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-6 px-4 py-4 sm:px-6 lg:px-8">
          <Link to="/" aria-label="B.E.A.M. home">
            <BrandMark compact />
          </Link>

          <nav className="hidden items-center gap-2 md:flex">
            {publicNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  classNames(
                    'rounded-2xl px-4 py-2 text-sm font-medium transition',
                    isActive
                      ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-950'
                      : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900',
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <ThemeToggle className="hidden sm:inline-flex" />
            <Link to="/dashboard" className={buttonClassName('secondary')}>
              Open dashboard
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-10">
        <Outlet />
      </main>

      <footer className="relative z-10 border-t border-slate-200/70 bg-white/75 backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-950/50">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-3 px-4 py-6 text-sm text-slate-500 sm:px-6 lg:px-8 md:flex-row md:items-center md:justify-between dark:text-slate-400">
          <p>© 2026 B.E.A.M. Behavioral Emotion Analysis Model</p>
          <p>Built with React, Vite, TailwindCSS, and FastAPI.</p>
        </div>
      </footer>
    </div>
  )
}