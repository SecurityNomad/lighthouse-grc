import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import type { User } from '../api/auth'

interface AuthState {
  token: string | null
  user: User | null
}

interface AuthContextType extends AuthState {
  login: (token: string, user: User) => void
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem('lh_token')
    const userStr = localStorage.getItem('lh_user')
    return {
      token,
      user: userStr ? JSON.parse(userStr) : null,
    }
  })

  const login = useCallback((token: string, user: User) => {
    localStorage.setItem('lh_token', token)
    localStorage.setItem('lh_user', JSON.stringify(user))
    setState({ token, user })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('lh_token')
    localStorage.removeItem('lh_user')
    localStorage.removeItem('lh_client_id')
    setState({ token: null, user: null })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, logout, isAuthenticated: !!state.token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
