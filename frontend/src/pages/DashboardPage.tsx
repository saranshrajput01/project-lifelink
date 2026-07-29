import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

export function DashboardPage() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      {/* Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
            <span className="text-white font-black text-base">L</span>
          </div>
          <span className="text-xl font-black bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">LIFELINK</span>
        </div>
        <motion.button
          onClick={handleLogout}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 text-gray-400 hover:text-red-400 font-medium transition-colors border border-white/5 rounded-xl hover:border-red-500/20 hover:bg-red-500/5"
        >
          Logout
        </motion.button>
      </nav>

      {/* Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-8 py-10">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-black text-white mb-1">Welcome to LIFELINK</h1>
          <p className="text-gray-400 mb-10">Your AI-powered health intelligence dashboard</p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-10">
          <StatCard title="Health Score" value="—" subtitle="Upload records to calculate" color="blue" icon="💙" delay={0.1} />
          <StatCard title="Documents" value="0" subtitle="Medical records uploaded" color="emerald" icon="📄" delay={0.2} />
          <StatCard title="Risk Alerts" value="0" subtitle="No alerts yet" color="yellow" icon="⚠️" delay={0.3} />
          <StatCard title="AI Insights" value="—" subtitle="Available after upload" color="purple" icon="🧠" delay={0.4} />
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            whileHover={{ y: -3, borderColor: 'rgba(59,130,246,0.3)' }}
            className="p-6 bg-white/[0.02] backdrop-blur-sm border border-white/[0.06] rounded-2xl transition-all"
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">📄</span>
              <h3 className="text-lg font-bold text-white">Upload Medical Records</h3>
            </div>
            <p className="text-gray-400 text-sm mb-5 leading-relaxed">
              Upload prescriptions, lab reports, or discharge summaries.
              AI will automatically extract and organize the information.
            </p>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/20 transition-all"
            >
              Upload Document
            </motion.button>
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
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-purple-500/20 transition-all"
            >
              Open AI Chat
            </motion.button>
          </motion.div>
        </div>

        {/* Timeline placeholder */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="mt-10 p-8 bg-white/[0.02] border border-white/[0.06] rounded-2xl text-center"
        >
          <span className="text-4xl mb-4 block">📈</span>
          <h3 className="text-lg font-bold text-white mb-2">Health Timeline</h3>
          <p className="text-gray-500 text-sm max-w-md mx-auto">
            Upload your first medical document to start building your AI-powered health timeline.
            Every report, prescription, and lab test will be tracked here.
          </p>
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
