import { Link } from 'react-router-dom'

export function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white/80 backdrop-blur-sm border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">L</span>
          </div>
          <span className="text-xl font-bold text-gray-900">LIFELINK</span>
        </div>
        <div className="flex gap-4">
          <Link to="/login" className="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium">
            Login
          </Link>
          <Link to="/register" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex items-center justify-center px-8">
        <div className="max-w-4xl text-center">
          <div className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-6">
            AI-Powered Healthcare Intelligence
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight mb-6">
            Your Complete Health
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">
              Intelligence Platform
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Securely store medical records. AI reads your reports, tracks your health timeline,
            and predicts risks before they become serious. Take control of your health.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/register" className="px-8 py-3 bg-blue-600 text-white rounded-xl text-lg font-semibold hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all">
              Start Free →
            </Link>
            <a href="#features" className="px-8 py-3 border border-gray-300 text-gray-700 rounded-xl text-lg font-semibold hover:bg-gray-50 transition-all">
              Learn More
            </a>
          </div>

          {/* Feature highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16" id="features">
            <FeatureCard
              icon="📄"
              title="AI Document Processing"
              description="Upload prescriptions & reports. AI extracts and organizes everything automatically."
            />
            <FeatureCard
              icon="📊"
              title="Health Predictions"
              description="ML models trained on real medical data predict health risks before they become serious."
            />
            <FeatureCard
              icon="🤖"
              title="AI Health Assistant"
              description="Ask questions about your reports. Get explanations in simple language."
            />
          </div>
        </div>
      </main>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  )
}
