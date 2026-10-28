import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { TimelinePage } from './pages/TimelinePage'
import { ProfilePage } from './pages/ProfilePage'
import { ChatPage } from './pages/ChatPage'
import { RemindersPage } from './pages/RemindersPage'
import { FamilyPage } from './pages/FamilyPage'
import { RiskPage } from './pages/RiskPage'
import { AdminPage } from './pages/AdminPage'
import { DoctorPage } from './pages/DoctorPage'
import { ProtectedRoute, RoleRoute } from './components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Patient routes */}
        <Route path="/dashboard" element={<RoleRoute allowed={['patient']}><DashboardPage /></RoleRoute>} />
        <Route path="/timeline" element={<ProtectedRoute><TimelinePage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
        <Route path="/reminders" element={<ProtectedRoute><RemindersPage /></ProtectedRoute>} />
        <Route path="/family" element={<ProtectedRoute><FamilyPage /></ProtectedRoute>} />
        <Route path="/risk" element={<ProtectedRoute><RiskPage /></ProtectedRoute>} />

        {/* Doctor route */}
        <Route path="/doctor" element={<RoleRoute allowed={['doctor']}><DoctorPage /></RoleRoute>} />

        {/* Admin route */}
        <Route path="/admin" element={<RoleRoute allowed={['admin']}><AdminPage /></RoleRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
