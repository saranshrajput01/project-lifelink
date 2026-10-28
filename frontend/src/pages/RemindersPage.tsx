import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface Reminder {
  id: string
  reminder_type: string
  title: string
  notes: string | null
  due_at: string
  recurrence: string
  is_done: boolean
}

const TYPES = ['medication', 'appointment', 'follow_up', 'test', 'custom']
const RECURRENCES = ['none', 'daily', 'weekly', 'monthly']

export function RemindersPage() {
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({
    title: '',
    reminder_type: 'medication',
    notes: '',
    due_at: '',
    recurrence: 'none',
  })
  const [saving, setSaving] = useState(false)

  const load = async () => {
    try {
      const res = await api.get('/reminders/')
      setReminders(res.data.reminders || [])
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const createReminder = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.title || !form.due_at) return
    setSaving(true)
    try {
      await api.post('/reminders/', {
        title: form.title,
        reminder_type: form.reminder_type,
        notes: form.notes || null,
        due_at: new Date(form.due_at).toISOString(),
        recurrence: form.recurrence,
      })
      setForm({ title: '', reminder_type: 'medication', notes: '', due_at: '', recurrence: 'none' })
      await load()
    } finally {
      setSaving(false)
    }
  }

  const markDone = async (id: string) => {
    await api.post(`/reminders/${id}/done`)
    await load()
  }

  const remove = async (id: string) => {
    await api.delete(`/reminders/${id}`)
    await load()
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
      </div>

      <nav className="relative z-10 flex items-center justify-between px-8 py-4 backdrop-blur-md border-b border-white/5">
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

      <main className="relative z-10 max-w-4xl mx-auto px-8 py-10">
        <h1 className="text-3xl font-black text-white mb-1">Reminders</h1>
        <p className="text-gray-400 mb-8">Medicine, appointments, and follow-ups — all in one place.</p>

        {/* Create form */}
        <form onSubmit={createReminder} className="mb-10 p-6 bg-white/[0.02] border border-white/[0.06] rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Title (e.g. Take Metformin)"
            className="md:col-span-2 bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/40"
          />
          <select
            value={form.reminder_type}
            onChange={(e) => setForm({ ...form, reminder_type: e.target.value })}
            className="bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/40"
          >
            {TYPES.map((t) => (
              <option key={t} value={t} className="bg-[#030014]">{t.replace('_', ' ')}</option>
            ))}
          </select>
          <select
            value={form.recurrence}
            onChange={(e) => setForm({ ...form, recurrence: e.target.value })}
            className="bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/40"
          >
            {RECURRENCES.map((r) => (
              <option key={r} value={r} className="bg-[#030014]">{r}</option>
            ))}
          </select>
          <input
            type="datetime-local"
            value={form.due_at}
            onChange={(e) => setForm({ ...form, due_at: e.target.value })}
            className="bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/40"
          />
          <input
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            placeholder="Notes (optional)"
            className="bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/40"
          />
          <motion.button
            type="submit"
            disabled={saving}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="md:col-span-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            {saving ? 'Adding…' : 'Add Reminder'}
          </motion.button>
        </form>

        {/* List */}
        {loading ? (
          <p className="text-gray-500 text-sm">Loading…</p>
        ) : reminders.length === 0 ? (
          <p className="text-gray-500 text-sm">No reminders yet. Add your first above.</p>
        ) : (
          <ul className="space-y-3">
            {reminders.map((r) => (
              <li
                key={r.id}
                className={`p-4 bg-white/[0.02] border border-white/[0.06] rounded-xl flex items-center justify-between gap-4 ${r.is_done ? 'opacity-50' : ''}`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 uppercase tracking-wider">
                      {r.reminder_type.replace('_', ' ')}
                    </span>
                    {r.recurrence !== 'none' && (
                      <span className="text-[10px] text-gray-500 uppercase">↻ {r.recurrence}</span>
                    )}
                  </div>
                  <p className={`text-sm font-semibold text-white mt-1 ${r.is_done ? 'line-through' : ''}`}>{r.title}</p>
                  <p className="text-xs text-gray-500">{new Date(r.due_at).toLocaleString()}</p>
                  {r.notes && <p className="text-xs text-gray-400 mt-1">{r.notes}</p>}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {!r.is_done && (
                    <button
                      onClick={() => markDone(r.id)}
                      className="px-3 py-1.5 text-xs font-medium text-emerald-300 border border-emerald-500/20 rounded-lg hover:bg-emerald-500/10 transition-colors"
                    >
                      Done
                    </button>
                  )}
                  <button
                    onClick={() => remove(r.id)}
                    className="px-3 py-1.5 text-xs font-medium text-red-300 border border-red-500/20 rounded-lg hover:bg-red-500/10 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  )
}
