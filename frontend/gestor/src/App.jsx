import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute, GestorRoute } from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Orders from './pages/Orders'
import Products from './pages/Products'
import Reports from './pages/Reports'
import Users from './pages/Users'
import ChatSessions from './pages/ChatSessions'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="pedidos" element={<Orders />} />
            <Route path="produtos" element={<Products />} />
            <Route path="atendimentos" element={<ChatSessions />} />
            <Route
              path="relatorios"
              element={
                <GestorRoute>
                  <Reports />
                </GestorRoute>
              }
            />
            <Route
              path="usuarios"
              element={
                <GestorRoute>
                  <Users />
                </GestorRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
