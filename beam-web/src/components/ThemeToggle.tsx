import { useTheme } from '../hooks/useTheme'
import { classNames } from '../utils/classNames'

type ThemeToggleProps = {
  className?: string
}

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={classNames(
        'inline-flex h-11 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800',
        className,
      )}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <>
          <span aria-hidden="true">☾</span>
          <span className="hidden sm:inline">Dark mode</span>
        </>
      ) : (
        <>
          <span aria-hidden="true">☀</span>
          <span className="hidden sm:inline">Light mode</span>
        </>
      )}
    </button>
  )
}