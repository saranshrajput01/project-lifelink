import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface Profile {
  date_of_birth: string
  gender: string
  blood_group: string
  height_cm: string
  weight_kg: string
  allergies: string
  chronic_conditions: string
  emergency_contact_name: string
  emergency_contact_phone: string
  address: string
}

interface UserInfo {
  full_name: string
  email: string
  role: string
}

export function ProfilePage() {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [profile, setProfile] = useState<Profile>({
    date_of_birth: '',
    gender: '',
    blood_group: '',
    height_cm: '',
    weight_kg: '',
    allergies: '',
    chronic_conditions: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    address: '',
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const meRes = await api.get('/auth/me')
        setUser(meRes.data)
      } catch {}

      try {
        const profileRes = await api.get('/profile/me')
        const p = profileRes.data
        setProfile({
          date_of_birth: p.date_of_birth || '',
          gender: p.gender || '',
          blood_group: p.blood_group || '',
          height_cm: p.height_cm ? String(p.height_cm) : '',
          weight_kg: p.weight_kg ? String(p.weight_kg) : '',
          allergies: p.allergies ? p.allergies.join(', ') : '',
          chronic_conditions: p.chronic_conditions ? p.chronic_conditions.join(', ') : '',
          emergency_contact_name: p.emergency_contact_name || '',
          emergency_contact_phone: p.emergency_contact_phone || '',
          address: p.address || '',
        })
      } catch {
        // No profile yet — form will be empty
      }
    }
    fetchData()
  }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage(null)

    try {
      const payload: any = {}
      if (profile.date_of_birth) payload.date_of_birth = profile.date_of_birth
      if (profile.gender) payload.gender = profile.gender
      if (profile.blood_group) payload.blood_group = profile.blood_group
      if (profile.height_cm) payload.height_cm = parseFloat(profile.height_cm)
      if (profile.weight_kg) payload.weight_kg = parseFloat(profile.weight_kg)
      if (profile.allergies) payload.allergies = profile.allergies.split(',').map(s => s.trim()).filter(Boolean)
      if (profile.chronic_conditions) payload.chronic_conditions = profile.chronic_conditions.split(',').map(s => s.trim()).filter(Boolean)
      if (profile.emergency_contact_name) payload.emergency_contact_name = profile.emergency_contact_name
      if (profile.emergency_contact_phone) payload.emergency_contact_phone = profile.emergency_contact_phone
      if (profile.address) payload.address = profile.address

      await api.put('/profile/me', payload)
      setMessage({ type: 'success', text: 'Profile saved successfully!' })
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to save profile' })
    } finally {
      setSaving(false)
    }
  }

  const inputClass = "w-full px-4 py-3 bg-white/[0.05] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all"
  const labelClass = "block text-sm font-medium text-gray-300 mb-2"

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
      </div>

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
            <span className="text-white font-black text-base">L</span>
          </div>
          <span className="text-xl font-black bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">LIFELINK</span>
        </div>
        <Link to="/dashboard" className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5">
          Dashboard
        </Link>
      </nav>

      {/* Content */}
      <main className="relative z-10 max-w-3xl mx-auto px-8 py-10">
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
          <h1 className="text-3xl font-black text-white mb-1">👤 My Profile</h1>
          <p className="text-gray-400 mb-8">Manage your health profile information</p>
        </motion.div>

        {/* User Info Card */}
        {user && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="mb-8 p-5 bg-white/[0.03] border border-white/[0.08] rounded-2xl flex items-center gap-4"
          >
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-2xl font-black">
              {user.full_name.charAt(0)}
            </div>
            <div>
              <p className="text-white font-bold text-lg">{user.full_name}</p>
              <p className="text-gray-400 text-sm">{user.email}</p>
              <span className="text-xs px-2 py-0.5 mt-1 inline-block bg-blue-500/20 text-blue-400 rounded-full">{user.role}</span>
            </div>
          </motion.div>
        )}

        {/* Profile Form */}
        <motion.form
          onSubmit={handleSave}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white/[0.03] border border-white/[0.08] rounded-2xl p-8 space-y-6"
        >
          {message && (
            <div className={`p-3 rounded-xl text-sm ${
              message.type === 'success'
                ? 'bg-green-500/10 border border-green-500/20 text-green-400'
                : 'bg-red-500/10 border border-red-500/20 text-red-400'
            }`}>
              {message.text}
            </div>
          )}

          {/* Row 1 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className={labelClass}>Date of Birth</label>
              <input type="date" value={profile.date_of_birth} onChange={e => setProfile({...profile, date_of_birth: e.target.value})} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Gender</label>
              <select value={profile.gender} onChange={e => setProfile({...profile, gender: e.target.value})} className={inputClass}>
                <option value="">Select</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Blood Group</label>
              <select value={profile.blood_group} onChange={e => setProfile({...profile, blood_group: e.target.value})} className={inputClass}>
                <option value="">Select</option>
                {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(bg => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Row 2 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className={labelClass}>Height (cm)</label>
              <input type="number" placeholder="170" value={profile.height_cm} onChange={e => setProfile({...profile, height_cm: e.target.value})} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Weight (kg)</label>
              <input type="number" placeholder="70" value={profile.weight_kg} onChange={e => setProfile({...profile, weight_kg: e.target.value})} className={inputClass} />
            </div>
          </div>

          {/* Row 3 */}
          <div>
            <label className={labelClass}>Allergies (comma separated)</label>
            <input type="text" placeholder="Penicillin, Dust, Peanuts" value={profile.allergies} onChange={e => setProfile({...profile, allergies: e.target.value})} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Chronic Conditions (comma separated)</label>
            <input type="text" placeholder="Diabetes, Hypertension" value={profile.chronic_conditions} onChange={e => setProfile({...profile, chronic_conditions: e.target.value})} className={inputClass} />
          </div>

          {/* Emergency Contact */}
          <div className="pt-4 border-t border-white/5">
            <h3 className="text-white font-semibold mb-4">🚨 Emergency Contact</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className={labelClass}>Contact Name</label>
                <input type="text" placeholder="Parent/Spouse name" value={profile.emergency_contact_name} onChange={e => setProfile({...profile, emergency_contact_name: e.target.value})} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Contact Phone</label>
                <input type="tel" placeholder="+91 98765 43210" value={profile.emergency_contact_phone} onChange={e => setProfile({...profile, emergency_contact_phone: e.target.value})} className={inputClass} />
              </div>
            </div>
          </div>

          {/* Address */}
          <div>
            <label className={labelClass}>Address</label>
            <textarea placeholder="Your address" value={profile.address} onChange={e => setProfile({...profile, address: e.target.value})} rows={3} className={inputClass} />
          </div>

          {/* Save Button */}
          <motion.button
            type="submit"
            disabled={saving}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 disabled:opacity-50 transition-all"
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </motion.button>
        </motion.form>
      </main>
    </div>
  )
}
