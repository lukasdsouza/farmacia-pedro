import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export function GestorRoute({ children }) {
  const { isAuthenticated, isGestor } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!isGestor) return <Navigate to="/dashboard" replace />
  return children
}
