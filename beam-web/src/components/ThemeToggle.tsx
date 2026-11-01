import { useTheme } from '../hooks/useTheme'
import { Moon, Sun } from 'lucide-react'

export function ThemeToggle({ className = '' }: { className?: string }) {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`relative inline-flex h-8 w-8 items-center justify-center rounded-lg border border-[#262626] bg-[#141414] text-[#B8B8B0] transition-all duration-150 hover:border-[#383838] hover:text-[#F5F5F0] hover:-translate-y-[1px] active:translate-y-[1px] ${className}`}
      aria-label="Toggle theme"
      title="Toggle theme mode"
    >
      {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
    </button>
  )
}
