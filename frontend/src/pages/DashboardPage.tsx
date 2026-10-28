import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { DocumentUpload } from '@/components/DocumentUpload'
import { api } from '@/services/api'

export function DashboardPage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState({ documents: 0, processed: 0, userName: '' })
  const [insights, setInsights] = useState<{ health_score: number | null; insights: string[] }>({
    health_score: null,
    insights: [],
  })

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [docsRes, meRes, insRes] = await Promise.all([
          api.get('/documents/?page_size=1'),
          api.get('/auth/me'),
          api.get('/documents/insights'),
        ])
        setStats({
          documents: insRes.data.total_documents ?? docsRes.data.total ?? 0,
          processed: insRes.data.processed_documents ?? 0,
          userName: meRes.data.full_name || '',
        })
        setInsights({
          health_score: insRes.data.health_score,
          insights: insRes.data.insights || [],
        })
      } catch {
        // silently fail
      }
    }
    fetchStats()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_name')
    navigate('/')
  }

  const [downloading, setDownloading] = useState(false)
  const handleDownloadReport = async () => {
    setDownloading(true)
    try {
      const res = await api.get('/documents/report/pdf', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = 'lifelink-health-report.pdf'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch {
      // ignore
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      {/* Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-4 sm:px-8 py-4 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
            <span className="text-white font-black text-base">L</span>
          </div>
          <span className="text-xl font-black bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">LIFELINK</span>
        </div>
        <div className="flex items-center gap-2 sm:gap-3 overflow-x-auto no-scrollbar -mx-4 px-4 sm:mx-0 sm:px-0 whitespace-nowrap">
          <Link
            to="/timeline"
            className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5"
          >
            Timeline
          </Link>
          <Link
            to="/reminders"
            className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5"
          >
            Reminders
          </Link>
          <Link
            to="/family"
            className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5"
          >
            Family
          </Link>
          <Link
            to="/risk"
            className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5"
          >
            Risk
          </Link>
          <Link
            to="/profile"
            className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5"
          >
            Profile
          </Link>
          <Link
            to="/"
            className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5"
          >
            Home
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

      {/* Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-8 py-8 sm:py-10">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-black text-white mb-1">
            {stats.userName ? `Welcome, ${stats.userName.split(' ')[0]}` : 'Welcome to LIFELINK'}
          </h1>
          <p className="text-gray-400 mb-10">Your AI-powered health intelligence dashboard</p>
        </motion.div>

        <div className="mb-8">
          <motion.button
            onClick={handleDownloadReport}
            disabled={downloading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-emerald-500/20 transition-all disabled:opacity-50"
          >
            {downloading ? 'Generating…' : '⬇ Download Health Report (PDF)'}
          </motion.button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-10">
          <StatCard title="Health Score" value={insights.health_score != null ? String(insights.health_score) : '—'} subtitle={insights.health_score != null ? 'Based on your records' : 'Upload records to calculate'} color="blue" icon="💙" delay={0.1} />
          <StatCard title="Documents" value={String(stats.documents)} subtitle="Medical records uploaded" color="emerald" icon="📄" delay={0.2} />
          <StatCard title="Processed" value={String(stats.processed)} subtitle="AI analyzed" color="yellow" icon="🧠" delay={0.3} />
          <StatCard title="AI Insights" value={String(insights.insights.length)} subtitle="Available after processing" color="purple" icon="✨" delay={0.4} />
        </div>

        {/* AI Insights panel */}
        {insights.insights.length > 0 && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.45, duration: 0.5 }}
            className="mb-10 p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl"
          >
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xl">✨</span>
              <h3 className="text-lg font-bold text-white">AI Insights</h3>
            </div>
            <ul className="space-y-2">
              {insights.insights.map((ins, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-blue-400 mt-0.5">•</span>
                  <span>{ins}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="p-6 bg-white/[0.02] backdrop-blur-sm border border-white/[0.06] rounded-2xl"
          >
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">📄</span>
              <h3 className="text-lg font-bold text-white">Upload Medical Records</h3>
            </div>
            <DocumentUpload />
          </motion.div>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            whileHover={{ y: -3, borderColor: 'rgba(139,92,246,0.3)' }}
            className="p-6 bg-white/[0.02] backdrop-blur-sm border border-white/[0.06] rounded-2xl transition-all"
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">🤖</span>
              <h3 className="text-lg font-bold text-white">Ask AI Assistant</h3>
            </div>
            <p className="text-gray-400 text-sm mb-5 leading-relaxed">
              Ask questions about your health, get report explanations,
              or explore your health timeline with AI.
            </p>
            <motion.button
              onClick={() => navigate('/chat')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-purple-500/20 transition-all"
            >
              Open AI Chat
            </motion.button>
          </motion.div>
        </div>

        {/* Timeline link */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="mt-10 p-8 bg-white/[0.02] border border-white/[0.06] rounded-2xl text-center"
        >
          <span className="text-4xl mb-4 block">📈</span>
          <h3 className="text-lg font-bold text-white mb-2">Health Timeline</h3>
          <p className="text-gray-500 text-sm max-w-md mx-auto mb-5">
            View all your medical records in chronological order — prescriptions, lab reports, and more.
          </p>
          <Link
            to="/timeline"
            className="inline-block px-6 py-2.5 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-purple-500/20 transition-all"
          >
            View Timeline →
          </Link>
        </motion.div>
      </main>
    </div>
  )
}

function StatCard({ title, value, subtitle, color, icon, delay }: { title: string; value: string; subtitle: string; color: string; icon: string; delay: number }) {
  const colors: Record<string, string> = {
    blue: 'from-blue-500/10 to-blue-900/5 border-blue-500/10',
    emerald: 'from-emerald-500/10 to-emerald-900/5 border-emerald-500/10',
    yellow: 'from-yellow-500/10 to-yellow-900/5 border-yellow-500/10',
    purple: 'from-purple-500/10 to-purple-900/5 border-purple-500/10',
  }
  const textColors: Record<string, string> = {
    blue: 'text-blue-400',
    emerald: 'text-emerald-400',
    yellow: 'text-yellow-400',
    purple: 'text-purple-400',
  }

  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{ scale: 1.02, borderColor: 'rgba(255,255,255,0.1)' }}
      className={`bg-gradient-to-br ${colors[color]} border rounded-2xl p-5 transition-all cursor-default`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-lg">{icon}</span>
        <span className="text-[10px] text-gray-600 uppercase tracking-wider">{title}</span>
      </div>
      <p className={`text-3xl font-black ${textColors[color]}`}>{value}</p>
      <p className="text-gray-500 text-xs mt-1">{subtitle}</p>
    </motion.div>
  )
}
