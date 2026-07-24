import { useEffect, useMemo, useState, type PropsWithChildren } from 'react'

import { loadThemePreference, saveThemePreference } from '../utils/storage'
import { ThemeContext, type ThemeContextValue, type Theme } from './theme-context'

function getSystemTheme(): Theme {
  if (typeof window === 'undefined') {
    return 'dark'
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setThemeState] = useState<Theme>(() => loadThemePreference() ?? getSystemTheme())

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', theme === 'dark')
    root.style.colorScheme = theme
    saveThemePreference(theme)
  }, [theme])

  const value = useMemo<ThemeContextValue>(() => ({
    theme,
    resolvedTheme: theme,
    setTheme: setThemeState,
    toggleTheme: () => setThemeState((currentTheme) => (currentTheme === 'dark' ? 'light' : 'dark')),
  }), [theme])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

