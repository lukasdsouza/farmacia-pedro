import { createContext, useContext, useState, useCallback } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('farmacia_user')
      return stored ? JSON.parse(stored) : null
    } catch { return null }
  })

  const login = useCallback(async (username, password) => {
    const res = await api.post('/auth/login', { username, password })
    const { access_token, refresh_token, role, nome_completo } = res.data
    const userData = { username, role, nome_completo, access_token, refresh_token }
    localStorage.setItem('farmacia_user', JSON.stringify(userData))
    localStorage.setItem('farmacia_token', access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    setUser(userData)
    return userData
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('farmacia_user')
    localStorage.removeItem('farmacia_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }, [])

  const isGestor = user?.role === 'gestor'

  // Restore token on mount
  const token = localStorage.getItem('farmacia_token')
  if (token && !api.defaults.headers.common['Authorization']) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isGestor, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
