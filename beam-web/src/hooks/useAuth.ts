import { useContext } from 'react'

import { AuthContext, type AuthContextValue } from '../contexts/auth-context'

export function useAuth(): AuthContextValue {
	const context = useContext(AuthContext)
	if (context === null) {
		throw new Error('useAuth must be used within AuthProvider')
	}

	return context
}