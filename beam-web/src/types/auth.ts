export type AuthTokens = {
  accessToken: string
  refreshToken: string
  tokenType: 'bearer'
}

export type AuthFormValues = {
  identifier: string
  password: string
}

export type RegisterFormValues = {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export type RegisterPayload = Omit<RegisterFormValues, 'confirmPassword'>

export type LoginResponse = {
  access_token: string
  refresh_token?: string | null
  token_type: string
}

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated'