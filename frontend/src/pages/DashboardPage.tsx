import { useNavigate } from 'react-router-dom'

export function DashboardPage() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen">
      {/* Top Navigation */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">L</span>
          </div>
          <span className="text-xl font-bold text-gray-900">LIFELINK</span>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 text-gray-600 hover:text-red-600 font-medium"
        >
          Logout
        </button>
      </nav>

      {/* Dashboard Content */}
      <main className="max-w-7xl mx-auto px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to LIFELINK</h1>
        <p className="text-gray-600 mb-8">Your AI-powered health intelligence dashboard</p>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard title="Health Score" value="—" subtitle="Upload records to calculate" color="blue" />
          <StatCard title="Documents" value="0" subtitle="Medical records uploaded" color="green" />
          <StatCard title="Risk Alerts" value="0" subtitle="No alerts yet" color="yellow" />
          <StatCard title="AI Insights" value="—" subtitle="Available after upload" color="purple" />
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">📄 Upload Medical Records</h3>
            <p className="text-gray-600 text-sm mb-4">
              Upload prescriptions, lab reports, or discharge summaries. 
              AI will automatically extract and organize the information.
            </p>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
              Upload Document (Coming Soon)
            </button>
          </div>
          <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">🤖 Ask AI Assistant</h3>
            <p className="text-gray-600 text-sm mb-4">
              Ask questions about your health, get report explanations,
              or explore your health timeline.
            </p>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
              Open Chat (Coming Soon)
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

function StatCard({ title, value, subtitle, color }: { title: string; value: string; subtitle: string; color: string }) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 border-blue-100',
    green: 'bg-green-50 border-green-100',
    yellow: 'bg-yellow-50 border-yellow-100',
    purple: 'bg-purple-50 border-purple-100',
  }

  return (
    <div className={`p-5 rounded-xl border ${colorClasses[color] || colorClasses.blue}`}>
      <p className="text-sm text-gray-600 font-medium">{title}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
    </div>
  )
}
