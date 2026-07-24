import { Link, NavLink, Outlet } from 'react-router-dom'

import { BrandMark } from '../components/BrandMark'
import { ThemeToggle } from '../components/ThemeToggle'
import { buttonClassName } from '../components/Button'
import { NavigationBar } from '../components/NavigationBar'
import { classNames } from '../utils/classNames'

const publicNavItems = [
  { to: '/', label: 'Home' },
  { to: '/login', label: 'Login' },
  { to: '/register', label: 'Register' },
]

export function PublicLayout() {
  return (
    <div className="kds-page relative min-h-screen overflow-hidden bg-[#050505] text-white">
      <NavigationBar
        brand={(
          <Link to="/" aria-label="B.E.A.M. home">
            <BrandMark compact />
          </Link>
        )}
        items={publicNavItems}
        actions={(
          <>
            <ThemeToggle className="hidden sm:inline-flex" />
            <Link to="/dashboard" className={buttonClassName('secondary')}>
              Open dashboard
            </Link>
          </>
        )}
      />

      <main className="relative z-10">
        <Outlet />
      </main>

      <footer className="relative z-10 border-t border-white/10 bg-[#050505]">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-3 px-4 py-6 text-sm text-white/56 sm:px-6 lg:px-8 md:flex-row md:items-center md:justify-between">
          <p>© 2026 B.E.A.M. Behavioral Emotion Analysis Model</p>
          <p>Built with React, Vite, TailwindCSS, and FastAPI.</p>
        </div>
      </footer>
    </div>
  )
}
