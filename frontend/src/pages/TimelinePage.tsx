import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface Document {
  id: string
  original_filename: string
  doc_type: string
  file_size_bytes: number
  uploaded_at: string
  ocr_status: string
  processing_status: string
  summary_short: string | null
  doctor_name: string | null
  hospital_name: string | null
  document_date: string | null
}

const docTypeIcons: Record<string, string> = {
  prescription: '💊',
  lab_report: '🧪',
  discharge_summary: '🏥',
  doctor_notes: '📝',
  vaccination: '💉',
  insurance: '📋',
  other: '📄',
}

const docTypeColors: Record<string, string> = {
  prescription: 'border-blue-500/30 bg-blue-500/5',
  lab_report: 'border-emerald-500/30 bg-emerald-500/5',
  discharge_summary: 'border-purple-500/30 bg-purple-500/5',
  doctor_notes: 'border-yellow-500/30 bg-yellow-500/5',
  vaccination: 'border-cyan-500/30 bg-cyan-500/5',
  insurance: 'border-orange-500/30 bg-orange-500/5',
  other: 'border-white/10 bg-white/[0.02]',
}

export function TimelinePage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const res = await api.get('/documents/?page_size=50')
        setDocuments(res.data.documents)
      } catch {
        // handle error
      } finally {
        setLoading(false)
      }
    }
    fetchDocs()
  }, [])

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white">
      {/* Background */}
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
        <div className="flex items-center gap-3">
          <Link to="/dashboard" className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5">
            Dashboard
          </Link>
        </div>
      </nav>

      {/* Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-8 py-10">
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
          <h1 className="text-3xl font-black text-white mb-1">📈 Health Timeline</h1>
          <p className="text-gray-400 mb-10">Your complete medical history in chronological order</p>
        </motion.div>

        {loading ? (
          <div className="text-center py-20 text-gray-500">Loading...</div>
        ) : documents.length === 0 ? (
          <div className="text-center py-20">
            <span className="text-5xl block mb-4">📭</span>
            <p className="text-gray-400">No documents yet. Upload medical records to build your timeline.</p>
            <Link to="/dashboard" className="inline-block mt-4 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold">
              Go to Dashboard
            </Link>
          </div>
        ) : (
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-blue-500/50 via-purple-500/30 to-transparent" />

            {/* Timeline items */}
            <div className="space-y-6">
              {documents.map((doc, index) => (
                <motion.div
                  key={doc.id}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative pl-16"
                >
                  {/* Dot */}
                  <div className="absolute left-4 top-5 w-5 h-5 rounded-full bg-[#030014] border-2 border-blue-500 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-blue-400" />
                  </div>

                  {/* Card */}
                  <div className={`p-5 border rounded-2xl ${docTypeColors[doc.doc_type] || docTypeColors['other']}`}>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">{docTypeIcons[doc.doc_type] || '📄'}</span>
                          <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                            {doc.doc_type.replace('_', ' ')}
                          </span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full ${
                            doc.processing_status === 'completed' 
                              ? 'bg-green-500/20 text-green-400' 
                              : 'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {doc.processing_status}
                          </span>
                        </div>
                        <h3 className="text-white font-semibold truncate">{doc.original_filename}</h3>
                        {doc.summary_short && (
                          <p className="text-gray-400 text-sm mt-1">{doc.summary_short}</p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          {doc.doctor_name && <span>👨‍⚕️ {doc.doctor_name}</span>}
                          {doc.hospital_name && <span>🏥 {doc.hospital_name}</span>}
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-sm text-gray-400">
                          {formatDate(doc.document_date || doc.uploaded_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
