import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { classNames } from '../../utils/classNames'
import { keycapClass } from '../keycap'

export type NavbarItem = {
  label: string
  /** Route path, e.g. "/#features" */
  to: string
}

type NavbarProps = {
  items?: NavbarItem[]
  signInTo?: string
  ctaLabel?: string
  ctaTo?: string
  className?: string
}

export function Navbar({
  items = [],
  signInTo = '/login',
  ctaLabel = 'START ANALYSIS →',
  ctaTo = '/analysis',
  className,
}: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    if (!menuOpen) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMenuOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [menuOpen])

  const closeMenu = () => setMenuOpen(false)

  return (
    <header
      className={classNames(
        'sticky top-0 z-40 border-b border-line-subtle bg-base/90 backdrop-blur-md',
        className,
      )}
    >
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:h-[72px] lg:px-8">
        {/* LEFT — wordmark + descriptor */}
        <Link to="/" className="group flex shrink-0 items-center gap-3" aria-label="B.E.A.M. home">
          <span
            className="kc pointer-events-none h-9 w-9 font-display text-base font-semibold text-lime shadow-none group-hover:-translate-y-px"
            aria-hidden="true"
          >
            B
          </span>
          <span className="flex flex-col leading-none">
            <span className="font-display text-lg font-semibold tracking-[0.08em] text-chalk">
              B.E.A.M.
            </span>
            <span className="mt-1 hidden text-[8px] font-medium uppercase tracking-[0.22em] text-dim sm:block">
              Behavioral Emotion Analysis Model
            </span>
          </span>
        </Link>

        {/* CENTER — section navigation */}
        {items.length > 0 ? (
          <nav aria-label="Primary" className="hidden items-center gap-1 rounded-module border border-line-subtle bg-surface p-1 lg:flex">
            {items.map((item) => (
              <Link
                key={item.label}
                to={item.to}
                className="rounded-keycap px-3.5 py-1.5 text-xs font-medium text-mist transition-colors duration-150 hover:bg-raised hover:text-chalk"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        ) : null}

        {/* RIGHT — actions */}
        <div className="hidden items-center gap-2.5 lg:flex">
          <Link to={signInTo} className={keycapClass('ghost', 'sm')}>
            Sign In
          </Link>
          <Link to={ctaTo} className={keycapClass('primary', 'sm')}>
            {ctaLabel}
          </Link>
        </div>

        {/* Mobile menu toggle */}
        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          className="kc h-9 w-9 lg:hidden"
          aria-expanded={menuOpen}
          aria-controls="beam-mobile-menu"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            {menuOpen ? <path d="M18 6L6 18M6 6l12 12" /> : <path d="M3 6h18M3 12h18M3 18h18" />}
          </svg>
        </button>
      </div>

      {/* Mobile panel */}
      {menuOpen ? (
        <div id="beam-mobile-menu" className="border-t border-line-subtle bg-deep px-4 pb-5 pt-3 sm:px-6 lg:hidden">
          <nav aria-label="Primary mobile" className="flex flex-col gap-1">
            {items.map((item) => (
              <Link
                key={item.label}
                to={item.to}
                onClick={closeMenu}
                className="rounded-keycap px-3 py-2.5 text-sm font-medium text-mist transition-colors duration-150 hover:bg-raised hover:text-chalk"
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="mt-4 flex flex-col gap-2.5 border-t border-line-subtle pt-4">
            <Link to={signInTo} onClick={closeMenu} className={keycapClass('ghost', 'md', 'w-full')}>
              Sign In
            </Link>
            <Link to={ctaTo} onClick={closeMenu} className={keycapClass('primary', 'md', 'w-full')}>
              {ctaLabel}
            </Link>
          </div>
        </div>
      ) : null}
    </header>
  )
}
