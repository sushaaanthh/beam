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
        'inline-flex h-11 items-center gap-3 rounded-[1rem] border border-white/10 bg-white/4 px-4 text-sm font-medium text-white/80 transition duration-200 hover:-translate-y-px hover:border-white/16 hover:bg-white/6 active:translate-y-px',
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