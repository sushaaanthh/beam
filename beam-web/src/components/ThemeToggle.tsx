import { useEffect, useState } from 'react'
import { useTheme } from '../hooks/useTheme'

export function ThemeToggle() {
  const { theme, toggleTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <button
        type="button"
        className="inline-flex h-10 w-10 items-center justify-center rounded-apple-md border border-apple-border bg-apple-bgCard text-apple-textSecondary"
        aria-label="Toggle theme"
        disabled
      >
        <span className="text-lg" aria-hidden="true">◐</span>
      </button>
    )
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="relative inline-flex h-10 w-10 items-center justify-center rounded-apple-md border border-apple-border bg-apple-bgCard text-apple-textSecondary transition-all duration-apple-fast ease-apple hover:border-apple-borderHover hover:bg-apple-bgCardHover hover:text-apple-textPrimary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-apple-accent focus-visible:ring-offset-2 focus-visible:ring-offset-apple-bg"
      aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
      aria-pressed={theme === 'dark'}
    >
      <span
        className="absolute transition-all duration-apple-normal ease-apple-spring"
        style={{
          opacity: resolvedTheme === 'dark' ? 1 : 0,
          transform: resolvedTheme === 'dark' ? 'rotate(0deg) scale(1)' : 'rotate(-90deg) scale(0.5)',
        }}
        aria-hidden="true"
      >
        🌙
      </span>
      <span
        className="absolute transition-all duration-apple-normal ease-apple-spring"
        style={{
          opacity: resolvedTheme === 'light' ? 1 : 0,
          transform: resolvedTheme === 'light' ? 'rotate(0deg) scale(1)' : 'rotate(90deg) scale(0.5)',
        }}
        aria-hidden="true"
      >
        ☀️
      </span>
    </button>
  )
}