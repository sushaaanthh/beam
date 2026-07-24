export type User = {
  id: string
  email: string
  username: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type UserRoleSummary = {
  title: string
  value: string
  description: string
}