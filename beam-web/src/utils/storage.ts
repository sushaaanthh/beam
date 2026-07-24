import type { AuthTokens } from '../types/auth'

const AUTH_STORAGE_KEY = 'beam.auth.tokens'
const THEME_STORAGE_KEY = 'beam.theme'
const AUTH_STORAGE_EVENT = 'beam-auth-tokens-changed'

type AuthTokensListener = (tokens: AuthTokens | null) => void

const authTokenListeners = new Set<AuthTokensListener>()

function canUseStorage() {
  return typeof window !== 'undefined' && typeof window.sessionStorage !== 'undefined'
}

export function loadAuthTokens(): AuthTokens | null {
  if (!canUseStorage()) {
    return null
  }

  const rawTokens = window.sessionStorage.getItem(AUTH_STORAGE_KEY)
  if (!rawTokens) {
    return null
  }

  try {
    return JSON.parse(rawTokens) as AuthTokens
  } catch {
    window.sessionStorage.removeItem(AUTH_STORAGE_KEY)
    return null
  }
}

export function saveAuthTokens(tokens: AuthTokens): void {
  if (!canUseStorage()) {
    return
  }

  window.sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(tokens))
  emitAuthTokensChange(tokens)
}

export function clearAuthTokens(): void {
  if (!canUseStorage()) {
    return
  }

  window.sessionStorage.removeItem(AUTH_STORAGE_KEY)
  emitAuthTokensChange(null)
}

export function subscribeAuthTokens(listener: AuthTokensListener): () => void {
  authTokenListeners.add(listener)
  return () => {
    authTokenListeners.delete(listener)
  }
}

export function loadThemePreference(): 'light' | 'dark' | null {
  if (!canUseStorage()) {
    return null
  }

  const theme = window.localStorage.getItem(THEME_STORAGE_KEY)
  return theme === 'light' || theme === 'dark' ? theme : null
}

export function saveThemePreference(theme: 'light' | 'dark'): void {
  if (!canUseStorage()) {
    return
  }

  window.localStorage.setItem(THEME_STORAGE_KEY, theme)
}

function emitAuthTokensChange(tokens: AuthTokens | null): void {
  if (!canUseStorage()) {
    return
  }

  window.dispatchEvent(new CustomEvent<AuthTokens | null>(AUTH_STORAGE_EVENT, { detail: tokens }))
  authTokenListeners.forEach((listener) => listener(tokens))
}

if (canUseStorage()) {
  window.addEventListener(AUTH_STORAGE_EVENT, (event) => {
    const detail = (event as CustomEvent<AuthTokens | null>).detail ?? null
    authTokenListeners.forEach((listener) => listener(detail))
  })
}