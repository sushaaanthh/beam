import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import { Footer } from '../components/global/Footer'
import { Navbar, type NavbarItem } from '../components/global/Navbar'

const publicNavItems: NavbarItem[] = [
  { label: 'Overview', to: '/#overview' },
  { label: 'Features', to: '/#features' },
  { label: 'Research', to: '/#research' },
  { label: 'Architecture', to: '/#architecture' },
  { label: 'Documentation', to: '/#documentation' },
]

export function PublicLayout() {
  const location = useLocation()

  // Smooth-scroll to hash targets after SPA navigation (e.g. from /login).
  useEffect(() => {
    if (!location.hash) return
    const target = document.getElementById(location.hash.slice(1))
    if (target) {
      requestAnimationFrame(() => {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      })
    }
  }, [location])

  return (
    <div className="relative flex min-h-screen flex-col bg-base text-chalk selection:bg-lime selection:text-base">
      <Navbar items={publicNavItems} />

      <main className="relative z-10 flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  )
}
