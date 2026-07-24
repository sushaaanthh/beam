import axios, { AxiosError, AxiosHeaders, type InternalAxiosRequestConfig } from 'axios'

import { API_V1_URL } from '../../utils/env'
import { clearAuthTokens, loadAuthTokens, saveAuthTokens } from '../../utils/storage'
import type { AuthTokens, LoginResponse } from '../../types/auth'

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean
}

const baseConfig = {
  baseURL: API_V1_URL,
  headers: {
    'Content-Type': 'application/json',
  },
}

export const authClient = axios.create(baseConfig)
export const apiClient = axios.create(baseConfig)

let refreshPromise: Promise<AuthTokens> | null = null

apiClient.interceptors.request.use((config) => {
  const tokens = loadAuthTokens()
  if (tokens?.accessToken) {
    const headers = AxiosHeaders.from(config.headers)
    headers.set('Authorization', `Bearer ${tokens.accessToken}`)
    config.headers = headers
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined
    const responseStatus = error.response?.status

    if (responseStatus !== 401 || originalRequest === undefined || originalRequest._retry) {
      return Promise.reject(error)
    }

    const refreshToken = loadAuthTokens()?.refreshToken
    if (!refreshToken) {
      clearAuthTokens()
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      refreshPromise ??= refreshAuthTokens(refreshToken)
      const refreshedTokens = await refreshPromise
      saveAuthTokens(refreshedTokens)

      const headers = AxiosHeaders.from(originalRequest.headers)
      headers.set('Authorization', `Bearer ${refreshedTokens.accessToken}`)
      originalRequest.headers = headers

      return apiClient(originalRequest)
    } catch (refreshError) {
      clearAuthTokens()
      return Promise.reject(refreshError)
    } finally {
      refreshPromise = null
    }
  },
)

async function refreshAuthTokens(refreshToken: string): Promise<AuthTokens> {
  const response = await authClient.post<LoginResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  })

  return normalizeTokens(response.data)
}

function normalizeTokens(response: LoginResponse): AuthTokens {
  return {
    accessToken: response.access_token,
    refreshToken: response.refresh_token ?? loadAuthTokens()?.refreshToken ?? '',
    tokenType: 'bearer',
  }
}

export function mapLoginResponse(response: LoginResponse): AuthTokens {
  return normalizeTokens(response)
}