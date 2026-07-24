import { useCallback, useEffect, useMemo, useState, type PropsWithChildren } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { fetchCurrentUser, loginRequest, logoutRequest, registerRequest } from '../services/api/auth'
import type { AuthFormValues, AuthStatus, AuthTokens, RegisterFormValues } from '../types/auth'
import { clearAuthTokens, loadAuthTokens, saveAuthTokens, subscribeAuthTokens } from '../utils/storage'
import { AuthContext, type AuthContextValue } from './auth-context'

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient()
  const [tokens, setTokens] = useState<AuthTokens | null>(() => loadAuthTokens())

  useEffect(() => subscribeAuthTokens(setTokens), [])

  const userQuery = useQuery({
    queryKey: ['current-user'],
    queryFn: fetchCurrentUser,
    enabled: tokens !== null,
  })

  useEffect(() => {
    if (userQuery.isError && tokens !== null) {
      clearAuthTokens()
      setTokens(null)
      queryClient.removeQueries({ queryKey: ['current-user'] })
    }
  }, [queryClient, tokens, userQuery.isError])

  const login = useCallback(async (values: AuthFormValues) => {
    const nextTokens = await loginRequest(values)
    saveAuthTokens(nextTokens)
    setTokens(nextTokens)
    const user = await queryClient.fetchQuery({
      queryKey: ['current-user'],
      queryFn: fetchCurrentUser,
    })
    return user
  }, [queryClient])

  const register = useCallback(async (values: RegisterFormValues) => {
    await registerRequest({
      username: values.username,
      email: values.email,
      password: values.password,
    })

    return login({ identifier: values.username, password: values.password })
  }, [login])

  const logout = useCallback(async () => {
    try {
      await logoutRequest(tokens?.refreshToken ?? null)
    } finally {
      clearAuthTokens()
      setTokens(null)
      queryClient.removeQueries({ queryKey: ['current-user'] })
    }
  }, [queryClient, tokens?.refreshToken])

  const value = useMemo<AuthContextValue>(() => {
    const isAuthenticated = userQuery.data !== undefined && tokens !== null
    const status: AuthStatus = tokens === null
      ? 'unauthenticated'
      : userQuery.isPending
        ? 'loading'
        : isAuthenticated
          ? 'authenticated'
          : 'unauthenticated'

    return {
      user: userQuery.data ?? null,
      tokens,
      status,
      isAuthenticated,
      isHydrating: tokens !== null && userQuery.isPending,
      login,
      register,
      logout,
    }
  }, [login, logout, register, tokens, userQuery.data, userQuery.isPending])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

