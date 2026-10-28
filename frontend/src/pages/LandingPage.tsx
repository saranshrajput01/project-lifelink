import { Link } from 'react-router-dom'
import { useEffect, useState, useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'

export function LandingPage() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll()
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0])
  const heroScale = useTransform(scrollYProgress, [0, 0.3], [1, 0.95])

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouse)
    return () => window.removeEventListener('mousemove', handleMouse)
  }, [])

  return (
    <div ref={containerRef} className="min-h-screen bg-[#030014] text-white overflow-x-hidden">
      {/* === ANIMATED BACKGROUND === */}
      {/* Mouse-following aurora */}
      <div
        className="pointer-events-none fixed inset-0 z-0"
        style={{
          background: `
            radial-gradient(800px circle at ${mousePos.x}px ${mousePos.y}px, rgba(59, 130, 246, 0.12), transparent 50%),
            radial-gradient(600px circle at ${mousePos.x - 200}px ${mousePos.y + 100}px, rgba(139, 92, 246, 0.08), transparent 50%)
          `,
        }}
      />

      {/* Animated orbs */}
      <div className="fixed inset-0 z-0 overflow-hidden">
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-blue-600/20 rounded-full blur-[128px] animate-[pulse_8s_ease-in-out_infinite]" />
        <div className="absolute top-3/4 -right-32 w-96 h-96 bg-purple-600/20 rounded-full blur-[128px] animate-[pulse_10s_ease-in-out_infinite_2s]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-[128px] animate-[pulse_12s_ease-in-out_infinite_4s]" />
      </div> 5                                     

      {/* Grid + Noise texture */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      {/* Floating particles */}
      <div className="fixed inset-0 z-0">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{
              width: `${Math.random() * 3 + 1}px`,
              height: `${Math.random() * 3 + 1}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: `rgba(${100 + Math.random() * 155}, ${150 + Math.random() * 105}, 255, ${0.4 + Math.random() * 0.4})`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.3, 1, 0.3],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 5,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      {/* === NAVIGATION === */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="relative z-20 flex items-center justify-between px-8 py-5 backdrop-blur-md border-b border-white/5"
      >
        <div className="flex items-center gap-3">
          <div className="relative group">
            <div className="w-11 h-11 bg-gradient-to-br from-blue-500 via-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
              <span className="text-white font-black text-lg">L</span>
            </div>
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl blur-xl opacity-40 group-hover:opacity-70 transition-opacity" />
          </div>
          <span className="text-2xl font-black tracking-tight bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent">
            LIFELINK
          </span>
        </div>
        <div className="flex gap-3 items-center">
          <Link to="/login" className="px-5 py-2.5 text-gray-300 hover:text-white font-medium transition-all hover:bg-white/5 rounded-xl">
            Login
          </Link>
          <Link to="/register" className="relative group px-6 py-2.5 font-semibold rounded-xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500" />
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-500 blur-xl opacity-40 group-hover:opacity-70 transition-opacity" />
            <span className="relative text-white text-sm">Get Started →</span>
          </Link>
        </div>
      </motion.nav>

      {/* === HERO SECTION === */}
      <motion.section style={{ opacity: heroOpacity, scale: heroScale }} className="relative z-10 flex flex-col items-center pt-24 pb-32 px-8">
        {/* Status badge */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="mb-8"
        >
          <div className="flex items-center gap-2 px-5 py-2.5 bg-white/5 border border-white/10 rounded-full backdrop-blur-sm">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-400" />
            </span>
            <span className="text-sm font-medium text-gray-300">Trained on Real Medical Datasets — MIMIC-IV & UCI</span>
          </div>
        </motion.div>

        {/* Main heading */}
        <motion.h1
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="text-6xl md:text-8xl font-black text-center leading-[1.1] tracking-tight mb-8"
        >
          <span className="block text-white">The Future of</span>
          <span className="block mt-2 bg-gradient-to-r from-blue-400 via-cyan-300 to-purple-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-[shimmer_3s_linear_infinite]">
            Health Intelligence
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="text-lg md:text-xl text-gray-400 text-center max-w-2xl mb-12 leading-relaxed"
        >
          Upload medical records. AI reads, extracts, and predicts health risks.
          <br className="hidden md:block" />
          <span className="text-gray-300">Your complete health timeline — powered by world-class ML.</span>
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 mb-20"
        >
          <Link to="/register" className="group relative px-10 py-4 font-bold text-lg rounded-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 group-hover:scale-[1.02] transition-transform" />
            <div className="absolute inset-[-2px] bg-gradient-to-r from-blue-600 to-cyan-500 rounded-2xl blur-xl opacity-40 group-hover:opacity-70 transition-opacity" />
            <span className="relative text-white flex items-center gap-2">
              Launch Your Health AI
              <motion.span animate={{ x: [0, 5, 0] }} transition={{ repeat: Infinity, duration: 1.5 }}>→</motion.span>
            </span>
          </Link>
          <a href="#features" className="px-10 py-4 border border-white/10 text-gray-300 rounded-2xl text-lg font-semibold hover:bg-white/5 hover:border-white/20 transition-all backdrop-blur-sm text-center">
            See How It Works
          </a>
        </motion.div>

        {/* === ANIMATED DASHBOARD PREVIEW === */}
        <DashboardPreview />
      </motion.section>

      {/* === FEATURES SECTION === */}
      <section id="features" className="relative z-10 py-32 px-8">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            Enterprise-Grade <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">AI Features</span>
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">Not a toy project — real ML models, real data, real predictions.</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <FeatureCard
            icon="🧬"
            title="OCR + NLP Pipeline"
            description="PaddleOCR reads handwritten prescriptions. GPT-4/Gemini extracts medications, diagnoses, lab values into structured JSON."
            stats="95% accuracy on printed docs"
            delay={0}
          />
          <FeatureCard
            icon="📊"
            title="Disease Risk Prediction"
            description="XGBoost models trained on MIMIC-IV (300K+ patients) and UCI datasets. SHAP explainability for every prediction."
            stats="AUC-ROC > 0.85 target"
            delay={0.1}
          />
          <FeatureCard
            icon="🤖"
            title="RAG Health Assistant"
            description="LangChain + pgvector. Ask questions about YOUR medical records. Every answer comes with source citations."
            stats="Context-aware medical AI"
            delay={0.2}
          />
          <FeatureCard
            icon="📈"
            title="Health Timeline"
            description="Every doctor visit, lab test, medication — automatically mapped to a chronological timeline with trend analysis."
            stats="Complete medical history view"
            delay={0.3}
          />
          <FeatureCard
            icon="🔐"
            title="Military-Grade Security"
            description="AES-256 encryption, field-level PII protection, RBAC, audit trails. You control who sees your data."
            stats="HIPAA-aligned architecture"
            delay={0.4}
          />
          <FeatureCard
            icon="☁️"
            title="Cloud-Native"
            description="Docker + AWS (ECS, RDS, S3). Auto-scaling, multi-AZ deployment. 99.9% uptime. GitHub Actions CI/CD."
            stats="Production-ready infrastructure"
            delay={0.5}
          />
        </div>
      </section>

      {/* === TECH STACK === */}
      <section className="relative z-10 py-20 px-8 border-t border-white/5">
        <p className="text-center text-gray-500 text-xs uppercase tracking-[0.3em] mb-8">Technology Stack</p>
        <div className="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto">
          {['Python', 'FastAPI', 'React', 'TypeScript', 'PostgreSQL', 'pgvector', 'XGBoost', 'LangChain', 'PaddleOCR', 'Docker', 'AWS', 'Redis', 'Celery', 'Scikit-learn'].map((tech, i) => (
            <motion.span
              key={tech}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ scale: 1.1, borderColor: 'rgba(59,130,246,0.5)' }}
              className="px-4 py-2 bg-white/[0.03] border border-white/10 rounded-lg text-sm text-gray-400 cursor-default transition-colors hover:text-white"
            >
              {tech}
            </motion.span>
          ))}
        </div>
      </section>

      {/* === FOOTER === */}
      <footer className="relative z-10 border-t border-white/5 py-10 text-center">
        <p className="text-gray-500 text-sm">© 2026 Project LIFELINK — Built by <span className="text-gray-300">Saransh Rajput</span></p>
        <p className="mt-2 text-gray-600 text-xs">AI-Powered Predictive & Connected Healthcare Intelligence Platform</p>
      </footer>

      {/* === GLOBAL ANIMATIONS === */}
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% center; }
          100% { background-position: -200% center; }
        }
      `}</style>
    </div>
  )
}

/* === DASHBOARD PREVIEW COMPONENT === */
function DashboardPreview() {
  return (
    <motion.div
      initial={{ y: 60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 1, duration: 1, ease: "easeOut" }}
      className="relative w-full max-w-5xl"
    >
      {/* Glow behind the card */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-cyan-500/10 rounded-3xl blur-3xl scale-105" />
      
      {/* Main card */}
      <div className="relative bg-[#0d1117]/80 backdrop-blur-2xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl shadow-blue-500/5">
        {/* Top bar */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>
          <span className="text-xs text-gray-600 font-mono">lifelink.ai/dashboard</span>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard value="92" label="Health Score" trend="+5" color="emerald" />
          <StatCard value="2" label="Risk Alerts" trend="–1" color="yellow" />
          <StatCard value="24" label="Documents" trend="+3" color="blue" />
          <StatCard value="156" label="Data Points" trend="+12" color="purple" />
        </div>

        {/* Chart area */}
        <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm font-medium text-gray-300">Health Score Trend</span>
            <span className="text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded-md">↑ 12% this quarter</span>
          </div>
          <div className="h-40 flex items-end gap-[6px]">
            {[35, 42, 38, 55, 48, 62, 58, 71, 65, 78, 72, 85, 80, 92, 88, 92].map((h, i) => (
              <motion.div
                key={i}
                className="flex-1 rounded-t-sm relative group cursor-pointer"
                initial={{ height: 0 }}
                animate={{ height: `${h}%` }}
                transition={{ delay: 1.2 + i * 0.08, duration: 0.6, ease: "easeOut" }}
                style={{
                  background: `linear-gradient(to top, rgba(59, 130, 246, 0.9), rgba(6, 182, 212, 0.4), transparent)`,
                }}
              >
                <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
                  {h}
                </div>
              </motion.div>
            ))}
          </div>
          <div className="flex justify-between mt-3">
            <span className="text-[10px] text-gray-600">Jan</span>
            <span className="text-[10px] text-gray-600">Apr</span>
            <span className="text-[10px] text-gray-600">Jul</span>
            <span className="text-[10px] text-gray-600">Now</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function StatCard({ value, label, trend, color }: { value: string; label: string; trend: string; color: string }) {
  const colors: Record<string, string> = {
    emerald: 'from-emerald-500/20 to-emerald-900/10 border-emerald-500/20 text-emerald-400',
    yellow: 'from-yellow-500/20 to-yellow-900/10 border-yellow-500/20 text-yellow-400',
    blue: 'from-blue-500/20 to-blue-900/10 border-blue-500/20 text-blue-400',
    purple: 'from-purple-500/20 to-purple-900/10 border-purple-500/20 text-purple-400',
  }
  const textColor: Record<string, string> = {
    emerald: 'text-emerald-400',
    yellow: 'text-yellow-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
  }
  return (
    <div className={`bg-gradient-to-br ${colors[color]} border rounded-xl p-4`}>
      <div className="flex items-baseline justify-between">
        <p className={`text-2xl font-black ${textColor[color]}`}>{value}</p>
        <span className="text-[10px] text-green-400">{trend}</span>
      </div>
      <p className="text-gray-500 text-xs mt-1">{label}</p>
    </div>
  )
}

function FeatureCard({ icon, title, description, stats, delay }: { icon: string; title: string; description: string; stats: string; delay: number }) {
  return (
    <motion.div
      initial={{ y: 30, opacity: 0 }}
      whileInView={{ y: 0, opacity: 1 }}
      viewport={{ once: true }}
      transition={{ delay, duration: 0.6 }}
      whileHover={{ y: -5, borderColor: 'rgba(59,130,246,0.3)' }}
      className="group p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl transition-all duration-300 hover:bg-white/[0.04]"
    >
      <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">{icon}</div>
      <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed mb-4">{description}</p>
      <div className="flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
        <span className="text-xs text-blue-400 font-medium">{stats}</span>
      </div>
    </motion.div>
  )
}
