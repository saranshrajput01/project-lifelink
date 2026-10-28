import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface FamilyMember {
  id: string
  full_name: string
  relationship: string
  date_of_birth: string | null
  gender: string | null
  blood_group: string | null
  allergies: string | null
  conditions: string | null
  emergency_contact: string | null
  notes: string | null
}

const RELATIONSHIPS = ['spouse', 'mother', 'father', 'son', 'daughter', 'sibling', 'guardian', 'other']
const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const emptyForm = {
  full_name: '',
  relationship: 'other',
  date_of_birth: '',
  gender: '',
  blood_group: '',
  allergies: '',
  conditions: '',
  emergency_contact: '',
  notes: '',
}

export function FamilyPage() {
  const [members, setMembers] = useState<FamilyMember[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ ...emptyForm })
  const [saving, setSaving] = useState(false)

  const load = async () => {
    try {
      const res = await api.get('/family/')
      setMembers(res.data.members || [])
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const createMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.full_name) return
    setSaving(true)
    try {
      await api.post('/family/', {
        full_name: form.full_name,
        relationship: form.relationship,
        date_of_birth: form.date_of_birth || null,
        gender: form.gender || null,
        blood_group: form.blood_group || null,
        allergies: form.allergies || null,
        conditions: form.conditions || null,
        emergency_contact: form.emergency_contact || null,
        notes: form.notes || null,
      })
      setForm({ ...emptyForm })
      await load()
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id: string) => {
    await api.delete(`/family/${id}`)
    await load()
  }

  const age = (dob: string | null) => {
    if (!dob) return null
    const diff = Date.now() - new Date(dob).getTime()
    return Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25))
  }

  const inputCls =
    'bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/40'

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
        <h1 className="text-2xl sm:text-3xl font-black text-white mb-1">Family Health Profiles</h1>
        <p className="text-gray-400 mb-8 text-sm sm:text-base">Manage health records for your family members — all under one account.</p>

        {/* Create form */}
        <form onSubmit={createMember} className="mb-10 p-5 sm:p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            value={form.full_name}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            placeholder="Full name"
            className={`md:col-span-2 ${inputCls}`}
          />
          <select value={form.relationship} onChange={(e) => setForm({ ...form, relationship: e.target.value })} className={inputCls}>
            {RELATIONSHIPS.map((r) => (
              <option key={r} value={r} className="bg-[#030014]">{r}</option>
            ))}
          </select>
          <select value={form.blood_group} onChange={(e) => setForm({ ...form, blood_group: e.target.value })} className={inputCls}>
            <option value="" className="bg-[#030014]">Blood group</option>
            {BLOOD_GROUPS.map((b) => (
              <option key={b} value={b} className="bg-[#030014]">{b}</option>
            ))}
          </select>
          <input type="date" value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} className={inputCls} />
          <input value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} placeholder="Gender" className={inputCls} />
          <input value={form.allergies} onChange={(e) => setForm({ ...form, allergies: e.target.value })} placeholder="Allergies (optional)" className={inputCls} />
          <input value={form.conditions} onChange={(e) => setForm({ ...form, conditions: e.target.value })} placeholder="Conditions (optional)" className={inputCls} />
          <input value={form.emergency_contact} onChange={(e) => setForm({ ...form, emergency_contact: e.target.value })} placeholder="Emergency contact (optional)" className={`md:col-span-2 ${inputCls}`} />
          <motion.button
            type="submit"
            disabled={saving}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="md:col-span-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            {saving ? 'Adding…' : 'Add Family Member'}
          </motion.button>
        </form>

        {/* List */}
        {loading ? (
          <p className="text-gray-500 text-sm">Loading…</p>
        ) : members.length === 0 ? (
          <p className="text-gray-500 text-sm">No family members yet. Add your first above.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {members.map((m) => (
              <div key={m.id} className="p-5 bg-white/[0.02] border border-white/[0.06] rounded-2xl">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-base font-bold text-white">{m.full_name}</p>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 uppercase tracking-wider">
                      {m.relationship}
                    </span>
                  </div>
                  {m.blood_group && (
                    <span className="text-xs px-2.5 py-1 rounded-lg bg-red-500/10 text-red-300 font-semibold">{m.blood_group}</span>
                  )}
                </div>
                <div className="mt-3 space-y-1 text-xs text-gray-400">
                  {m.date_of_birth && <p>DOB: {new Date(m.date_of_birth).toLocaleDateString()} ({age(m.date_of_birth)} yrs)</p>}
                  {m.gender && <p>Gender: {m.gender}</p>}
                  {m.allergies && <p className="text-amber-300/80">Allergies: {m.allergies}</p>}
                  {m.conditions && <p>Conditions: {m.conditions}</p>}
                  {m.emergency_contact && <p>Emergency: {m.emergency_contact}</p>}
                </div>
                <button
                  onClick={() => remove(m.id)}
                  className="mt-4 px-3 py-1.5 text-xs font-medium text-red-300 border border-red-500/20 rounded-lg hover:bg-red-500/10 transition-colors"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
