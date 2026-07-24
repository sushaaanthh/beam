import { apiClient, authClient, mapLoginResponse } from './http'
import type { AuthFormValues, AuthTokens, LoginResponse, RegisterPayload } from '../../types/auth'
import type { User } from '../../types/user'

export async function loginRequest(values: AuthFormValues): Promise<AuthTokens> {
  const body = new URLSearchParams({
    username: values.identifier,
    password: values.password,
  })

  const response = await authClient.post<LoginResponse>('/auth/login', body, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })

  return mapLoginResponse(response.data)
}

export async function registerRequest(values: RegisterPayload): Promise<void> {
  await authClient.post('/auth/register', values)
}

export async function logoutRequest(refreshToken: string | null): Promise<void> {
  await apiClient.post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : {})
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>('/users/me')
  return response.data
}