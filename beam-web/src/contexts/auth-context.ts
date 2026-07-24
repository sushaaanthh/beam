import { createContext } from 'react'

import type { AuthFormValues, AuthStatus, AuthTokens, RegisterFormValues } from '../types/auth'
import type { User } from '../types/user'

export type AuthContextValue = {
  user: User | null
  tokens: AuthTokens | null
  status: AuthStatus
  isAuthenticated: boolean
  isHydrating: boolean
  login: (values: AuthFormValues) => Promise<User>
  register: (values: RegisterFormValues) => Promise<User>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)