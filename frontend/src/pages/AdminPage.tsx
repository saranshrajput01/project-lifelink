import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface Stats {
  total_users: number
  total_documents: number
  processed_documents: number
  pending_documents: number
}

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

interface Document {
  id: string
  patient_id: string
  original_filename: string
  doc_type: string
  file_size_bytes: number
  processing_status: string
  uploaded_at: string
}

export function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [activeTab, setActiveTab] = useState<'users' | 'documents'>('users')
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, usersRes, docsRes] = await Promise.all([
          api.get('/admin/stats'),
          api.get('/admin/users'),
          api.get('/admin/documents'),
        ])
        setStats(statsRes.data)
        setUsers(usersRes.data.users)
        setDocuments(docsRes.data.documents)
      } catch (err: unknown) {
        const e = err as { response?: { status?: number } }
        if (e.response?.status === 403) {
          setError('Access denied. Admin role required.')
        } else {
          setError('Failed to load admin data.')
        }
      }
    }
    fetchData()
  }, [])

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#030014] text-white flex items-center justify-center">
        <div className="text-center">
          <span className="text-5xl block mb-4">🚫</span>
          <p className="text-red-400 text-lg font-semibold">{error}</p>
          <Link to="/dashboard" className="inline-block mt-4 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-red-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-orange-600/10 rounded-full blur-[128px]" />
      </div>

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-red-500 via-orange-400 to-yellow-500 rounded-xl flex items-center justify-center shadow-lg shadow-red-500/25">
            <span className="text-white font-black text-base">A</span>
          </div>
          <span className="text-xl font-black bg-gradient-to-r from-white to-orange-200 bg-clip-text text-transparent">ADMIN PANEL</span>
        </div>
        <Link to="/dashboard" className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5">
          Dashboard
        </Link>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-8 py-10">
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
          <h1 className="text-3xl font-black text-white mb-1">⚙️ Admin Panel</h1>
          <p className="text-gray-400 mb-8">Platform management & analytics</p>
        </motion.div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-10">
            <StatCard label="Total Users" value={stats.total_users} icon="👥" color="blue" />
            <StatCard label="Total Documents" value={stats.total_documents} icon="📄" color="emerald" />
            <StatCard label="Processed" value={stats.processed_documents} icon="✅" color="green" />
            <StatCard label="Pending" value={stats.pending_documents} icon="⏳" color="yellow" />
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'users' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'text-gray-400 border border-white/5 hover:bg-white/5'
            }`}
          >
            👥 Users ({users.length})
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'documents' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-gray-400 border border-white/5 hover:bg-white/5'
            }`}
          >
            📄 Documents ({documents.length})
          </button>
        </div>

        {/* Users Table */}
        {activeTab === 'users' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white/[0.02] border border-white/[0.06] rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">User</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Role</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-white/[0.03] hover:bg-white/[0.02]">
                    <td className="px-5 py-4">
                      <p className="text-white font-medium text-sm">{user.full_name}</p>
                      <p className="text-gray-500 text-xs">{user.email}</p>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        user.role === 'admin' ? 'bg-red-500/20 text-red-400' :
                        user.role === 'doctor' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`text-xs ${user.is_active ? 'text-green-400' : 'text-red-400'}`}>
                        {user.is_active ? '● Active' : '● Inactive'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-gray-400 text-sm">{formatDate(user.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}

        {/* Documents Table */}
        {activeTab === 'documents' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white/[0.02] border border-white/[0.06] rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">File</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Size</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 uppercase tracking-wider">Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} className="border-b border-white/[0.03] hover:bg-white/[0.02]">
                    <td className="px-5 py-4 text-white text-sm font-medium truncate max-w-[200px]">{doc.original_filename}</td>
                    <td className="px-5 py-4 text-gray-400 text-sm">{doc.doc_type.replace('_', ' ')}</td>
                    <td className="px-5 py-4 text-gray-400 text-sm">{formatSize(doc.file_size_bytes)}</td>
                    <td className="px-5 py-4">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        doc.processing_status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        doc.processing_status === 'failed' ? 'bg-red-500/20 text-red-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {doc.processing_status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-gray-400 text-sm">{formatDate(doc.uploaded_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}
      </main>
    </div>
  )
}

function StatCard({ label, value, icon, color }: { label: string; value: number; icon: string; color: string }) {
  const colors: Record<string, string> = {
    blue: 'from-blue-500/10 to-blue-900/5 border-blue-500/10',
    emerald: 'from-emerald-500/10 to-emerald-900/5 border-emerald-500/10',
    green: 'from-green-500/10 to-green-900/5 border-green-500/10',
    yellow: 'from-yellow-500/10 to-yellow-900/5 border-yellow-500/10',
  }
  const textColors: Record<string, string> = {
    blue: 'text-blue-400',
    emerald: 'text-emerald-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
  }
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
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
