import { Navigate } from 'react-router-dom'

// Basic auth guard — redirect to login if no token
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token')
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

// Role guard — redirect to correct dashboard if wrong role
export function RoleRoute({
  children,
  allowed,
}: {
  children: React.ReactNode
  allowed: string[]
}) {
  const token = localStorage.getItem('access_token')
  if (!token) return <Navigate to="/login" replace />

  const role = localStorage.getItem('user_role') || 'patient'
  if (!allowed.includes(role)) {
    if (role === 'admin') return <Navigate to="/admin" replace />
    if (role === 'doctor') return <Navigate to="/doctor" replace />
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}
