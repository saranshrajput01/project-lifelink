import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface Patient {
  id: string
  full_name: string
  email: string
  is_active: boolean
  created_at: string
}

export function DoctorPage() {
  const navigate = useNavigate()
  const doctorName = localStorage.getItem('user_name') || 'Doctor'
  const [patients, setPatients] = useState<Patient[]>([])
  const [totalDocs, setTotalDocs] = useState(0)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [usersRes, docsRes] = await Promise.all([
          api.get('/admin/users'),
          api.get('/admin/documents'),
        ])
        const patientList = usersRes.data.users.filter((u: Patient & { role: string }) => u.role === 'patient')
        setPatients(patientList)
        setTotalDocs(docsRes.data.documents?.length || 0)
      } catch {
        setError('Failed to load patient data.')
      }
    }
    fetchData()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_name')
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      {/* Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-teal-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[128px]" />
      </div>

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-teal-500 via-cyan-400 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-teal-500/25">
            <span className="text-white font-black text-base">D</span>
          </div>
          <span className="text-xl font-black bg-gradient-to-r from-white to-teal-200 bg-clip-text text-transparent">DOCTOR PORTAL</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/timeline" className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5">
            Timeline
          </Link>
          <Link to="/profile" className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5">
            My Profile
          </Link>
          <motion.button
            onClick={handleLogout}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 text-gray-400 hover:text-red-400 font-medium transition-colors border border-white/5 rounded-xl hover:border-red-500/20 hover:bg-red-500/5"
          >
            Logout
          </motion.button>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-8 py-10">
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5 }}>
          <h1 className="text-3xl font-black text-white mb-1">
            Welcome, Dr. {doctorName.split(' ')[0]} 👨‍⚕️
          </h1>
          <p className="text-gray-400 mb-10">Patient overview & health records</p>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          <StatCard label="Total Patients" value={patients.length} icon="🧑‍🤝‍🧑" color="teal" delay={0.1} />
          <StatCard label="Medical Records" value={totalDocs} icon="📄" color="blue" delay={0.2} />
          <StatCard label="Active Patients" value={patients.filter(p => p.is_active).length} icon="✅" color="green" delay={0.3} />
        </div>

        {/* Patient List */}
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.4 }}>
          <h2 className="text-lg font-bold text-white mb-4">🧑‍🤝‍🧑 Registered Patients</h2>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm mb-4">{error}</div>
          )}

          <div className="bg-white/[0.02] border border-white/[0.06] rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Patient</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Joined</th>
                </tr>
              </thead>
              <tbody>
                {patients.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-5 py-8 text-center text-gray-500 text-sm">No patients found</td>
                  </tr>
                ) : patients.map((patient) => (
                  <tr key={patient.id} className="border-b border-white/[0.03] hover:bg-white/[0.02]">
                    <td className="px-5 py-4 text-white font-medium text-sm">{patient.full_name}</td>
                    <td className="px-5 py-4 text-gray-400 text-sm">{patient.email}</td>
                    <td className="px-5 py-4">
                      <span className={`text-xs ${patient.is_active ? 'text-green-400' : 'text-red-400'}`}>
                        {patient.is_active ? '● Active' : '● Inactive'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-gray-400 text-sm">
                      {new Date(patient.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.5 }} className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">📈</span>
              <h3 className="text-lg font-bold text-white">Health Timeline</h3>
            </div>
            <p className="text-gray-400 text-sm mb-4">View chronological health records of patients.</p>
            <Link to="/timeline" className="inline-block px-5 py-2.5 bg-gradient-to-r from-teal-600 to-cyan-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-teal-500/20 transition-all">
              Open Timeline →
            </Link>
          </div>
          <div className="p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">👤</span>
              <h3 className="text-lg font-bold text-white">My Profile</h3>
            </div>
            <p className="text-gray-400 text-sm mb-4">Update your doctor profile and credentials.</p>
            <Link to="/profile" className="inline-block px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/20 transition-all">
              Edit Profile →
            </Link>
          </div>
        </motion.div>
      </main>
    </div>
  )
}

function StatCard({ label, value, icon, color, delay }: { label: string; value: number; icon: string; color: string; delay: number }) {
  const colors: Record<string, string> = {
    teal: 'from-teal-500/10 to-teal-900/5 border-teal-500/10',
    blue: 'from-blue-500/10 to-blue-900/5 border-blue-500/10',
    green: 'from-green-500/10 to-green-900/5 border-green-500/10',
  }
  const textColors: Record<string, string> = {
    teal: 'text-teal-400',
    blue: 'text-blue-400',
    green: 'text-green-400',
  }
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay, duration: 0.5 }}
      className={`bg-gradient-to-br ${colors[color]} border rounded-2xl p-5`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-lg">{icon}</span>
        <span className="text-[10px] text-gray-600 uppercase tracking-wider">{label}</span>
      </div>
      <p className={`text-3xl font-black ${textColors[color]}`}>{value}</p>
    </motion.div>
  )
}
