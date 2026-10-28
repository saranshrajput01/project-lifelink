import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface Factor {
  factor: string
  value: number
  impact: number
  direction: string
}

interface RiskResult {
  disease_type: string
  risk_score: number
  risk_level: string
  contributing_factors: Factor[]
  recommendations: string[]
  explanation: string
  model_version: string
  model_confidence: number | null
}

const LEVEL_COLOR: Record<string, string> = {
  low: 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10',
  moderate: 'text-amber-300 border-amber-500/30 bg-amber-500/10',
  high: 'text-orange-300 border-orange-500/30 bg-orange-500/10',
  critical: 'text-red-300 border-red-500/30 bg-red-500/10',
}

const inputCls =
  'w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/40'

export function RiskPage() {
  const [tab, setTab] = useState<'cardiovascular' | 'diabetes' | 'ckd'>('cardiovascular')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<RiskResult | null>(null)

  const [heart, setHeart] = useState({ age: 55, sex: 1, cholesterol: 220, systolic_bp: 135, smoker: 0, bmi: 27, diabetic: 0 })
  const [diab, setDiab] = useState({ glucose: 130, bmi: 30, age: 45, insulin: 110, diastolic_bp: 78, pregnancies: 1, family_history: 0 })
  const [ckd, setCkd] = useState({ age: 55, systolic_bp: 80, blood_glucose: 140, blood_urea: 50, serum_creatinine: 1.5, hemoglobin: 12, albumin: 1, hypertension: 0, diabetic: 0 })

  const run = async () => {
    setLoading(true)
    setResult(null)
    try {
      const payload = tab === 'cardiovascular' ? heart : tab === 'diabetes' ? diab : ckd
      const res = await api.post(`/predictions/${tab}`, payload)
      setResult(res.data)
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const num = (obj: any, set: any, key: string, label: string) => (
    <label className="block">
      <span className="text-xs text-gray-400">{label}</span>
      <input type="number" value={obj[key]} onChange={(e) => set({ ...obj, [key]: Number(e.target.value) })} className={inputCls} />
    </label>
  )

  const bool = (obj: any, set: any, key: string, label: string) => (
    <label className="block">
      <span className="text-xs text-gray-400">{label}</span>
      <select value={obj[key]} onChange={(e) => set({ ...obj, [key]: Number(e.target.value) })} className={inputCls}>
        <option value={0} className="bg-[#030014]">No</option>
        <option value={1} className="bg-[#030014]">Yes</option>
      </select>
    </label>
  )

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
      </div>

      <nav className="relative z-10 flex items-center justify-between px-4 sm:px-8 py-4 backdrop-blur-md border-b border-white/5">
        <Link to="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
            <span className="text-white font-black text-base">L</span>
          </div>
          <span className="text-xl font-black bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">LIFELINK</span>
        </Link>
        <Link to="/dashboard" className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5">
          ← Dashboard
        </Link>
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-4 sm:px-8 py-8 sm:py-10">
        <h1 className="text-2xl sm:text-3xl font-black text-white mb-1">Predictive Risk Analytics</h1>
        <p className="text-gray-400 mb-6 text-sm sm:text-base">ML-powered disease risk scoring with explainable contributing factors.</p>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {(['cardiovascular', 'diabetes', 'ckd'] as const).map((t) => (
            <button
              key={t}
              onClick={() => { setTab(t); setResult(null) }}
              className={`px-4 py-2 rounded-xl text-sm font-semibold border transition-all ${tab === t ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white border-transparent' : 'text-gray-400 border-white/10 hover:border-white/20'}`}
            >
              {t === 'cardiovascular' ? '❤️ Cardiovascular' : t === 'diabetes' ? '🩸 Diabetes' : '🫘 Kidney (CKD)'}
            </button>
          ))}
        </div>

        {/* Inputs */}
        <div className="p-5 sm:p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl grid grid-cols-2 md:grid-cols-3 gap-4 mb-5">
          {tab === 'cardiovascular' ? (
            <>
              {num(heart, setHeart, 'age', 'Age')}
              {bool(heart, setHeart, 'sex', 'Male')}
              {num(heart, setHeart, 'cholesterol', 'Cholesterol (mg/dL)')}
              {num(heart, setHeart, 'systolic_bp', 'Systolic BP')}
              {bool(heart, setHeart, 'smoker', 'Smoker')}
              {num(heart, setHeart, 'bmi', 'BMI')}
              {bool(heart, setHeart, 'diabetic', 'Diabetic')}
            </>
          ) : tab === 'diabetes' ? (
            <>
              {num(diab, setDiab, 'glucose', 'Glucose (mg/dL)')}
              {num(diab, setDiab, 'bmi', 'BMI')}
              {num(diab, setDiab, 'age', 'Age')}
              {num(diab, setDiab, 'insulin', 'Insulin')}
              {num(diab, setDiab, 'diastolic_bp', 'Diastolic BP')}
              {num(diab, setDiab, 'pregnancies', 'Pregnancies')}
              {bool(diab, setDiab, 'family_history', 'Family history')}
            </>
          ) : (
            <>
              {num(ckd, setCkd, 'age', 'Age')}
              {num(ckd, setCkd, 'systolic_bp', 'Blood pressure')}
              {num(ckd, setCkd, 'blood_glucose', 'Blood glucose')}
              {num(ckd, setCkd, 'blood_urea', 'Blood urea')}
              {num(ckd, setCkd, 'serum_creatinine', 'Serum creatinine')}
              {num(ckd, setCkd, 'hemoglobin', 'Hemoglobin')}
              {num(ckd, setCkd, 'albumin', 'Albumin (0-5)')}
              {bool(ckd, setCkd, 'hypertension', 'Hypertension')}
              {bool(ckd, setCkd, 'diabetic', 'Diabetic')}
            </>
          )}
        </div>

        <motion.button
          onClick={run}
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full px-5 py-3 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-blue-500/20 transition-all disabled:opacity-50 mb-8"
        >
          {loading ? 'Analysing…' : 'Calculate Risk'}
        </motion.button>

        {/* Result */}
        {result && (
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="space-y-5">
            <div className={`p-6 rounded-2xl border ${LEVEL_COLOR[result.risk_level] || LEVEL_COLOR.low}`}>
              <div className="flex items-end justify-between flex-wrap gap-3">
                <div>
                  <p className="text-xs uppercase tracking-wider opacity-70">Risk Level</p>
                  <p className="text-3xl font-black capitalize">{result.risk_level}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs uppercase tracking-wider opacity-70">Risk Score</p>
                  <p className="text-4xl font-black">{Math.round(result.risk_score * 100)}%</p>
                </div>
              </div>
              <div className="mt-4 h-2 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-current" style={{ width: `${Math.round(result.risk_score * 100)}%` }} />
              </div>
              <p className="text-sm mt-4 opacity-90">{result.explanation}</p>
              {result.model_confidence != null && (
                <p className="text-[11px] mt-2 opacity-60">Model: {result.model_version} · AUC {result.model_confidence}</p>
              )}
            </div>

            <div className="p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl">
              <h3 className="text-sm font-bold text-white mb-3">Contributing Factors</h3>
              <ul className="space-y-2">
                {result.contributing_factors.map((f, i) => (
                  <li key={i} className="flex items-center justify-between text-sm">
                    <span className="text-gray-300">{f.factor} <span className="text-gray-500">({f.value})</span></span>
                    <span className={f.direction === 'increases_risk' ? 'text-red-300' : 'text-emerald-300'}>
                      {f.direction === 'increases_risk' ? '↑ raises' : '↓ lowers'} · {f.impact}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl">
              <h3 className="text-sm font-bold text-white mb-3">Recommendations</h3>
              <ul className="space-y-2 list-disc list-inside text-sm text-gray-300">
                {result.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  )
}
