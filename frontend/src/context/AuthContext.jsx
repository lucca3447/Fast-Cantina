/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../services/api'

const AuthContext = createContext(null)

function normalizeRole(role) {
  if (role === 'atendente') {
    return 'funcionario'
  }
  return role
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  async function fetchMe() {
    const response = await api.get('/auth/me')
    setUser(response.data)
    return response.data
  }

  async function login(loginValue, senha) {
    await api.post('/auth/login', { login: loginValue, senha })
    return fetchMe()
  }

  async function loginDemo(perfil = 'admin') {
    await api.post('/auth/demo', { perfil })
    return fetchMe()
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } finally {
      setUser(null)
    }
  }

  function hasAnyRole(roles = []) {
    if (!user) {
      return false
    }

    const role = normalizeRole(user.perfil)
    return roles.includes(role)
  }

  useEffect(() => {
    let active = true

    async function bootstrap() {
      try {
        await fetchMe()
      } catch {
        if (active) {
          setUser(null)
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    bootstrap()

    const handleSessionExpired = () => {
      setUser(null)
    }

    window.addEventListener('auth:session-expired', handleSessionExpired)

    return () => {
      active = false
      window.removeEventListener('auth:session-expired', handleSessionExpired)
    }
  }, [])

  const isAuthenticated = Boolean(user)

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    loginDemo,
    logout,
    fetchMe,
    hasAnyRole,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider')
  }
  return context
}
