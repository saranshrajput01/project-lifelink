import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { api } from '@/services/api'

interface Document {
  id: string
  original_filename: string
  doc_type: string
  file_size_bytes: number
  uploaded_at: string
  ocr_status: string
}

export function DocumentUpload() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [docType, setDocType] = useState('other')
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents/')
      setDocuments(res.data.documents)
    } catch {
      // silently fail on list
    }
  }

  // Fetch on mount
  useState(() => { fetchDocuments() })

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    setUploading(true)
    setMessage(null)

    const file = files[0]
    const formData = new FormData()
    formData.append('file', file)

    try {
      await api.post(`/documents/upload?doc_type=${docType}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setMessage({ type: 'success', text: `"${file.name}" uploaded successfully!` })
      fetchDocuments()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Upload failed' })
    } finally {
      setUploading(false)
    }
  }

  const handleDownload = async (docId: string) => {
    try {
      const res = await api.get(`/documents/${docId}/download`)
      window.open(res.data.download_url, '_blank')
    } catch {
      setMessage({ type: 'error', text: 'Failed to get download link' })
    }
  }

  const handleDelete = async (docId: string) => {
    try {
      await api.delete(`/documents/${docId}`)
      setDocuments(documents.filter(d => d.id !== docId))
      setMessage({ type: 'success', text: 'Document deleted' })
    } catch {
      setMessage({ type: 'error', text: 'Failed to delete' })
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files) }}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
          dragOver
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-white/10 hover:border-white/20 hover:bg-white/[0.02]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.jpg,.jpeg,.png,.webp,.tiff"
          onChange={(e) => handleUpload(e.target.files)}
        />
        <span className="text-4xl block mb-3">{uploading ? '⏳' : '📁'}</span>
        <p className="text-white font-semibold">
          {uploading ? 'Uploading...' : 'Drop file here or click to upload'}
        </p>
        <p className="text-gray-500 text-sm mt-1">PDF, JPEG, PNG, WebP, TIFF — Max 50MB</p>
      </div>

      {/* Doc Type Selector */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-gray-400 text-sm">Type:</span>
        {['prescription', 'lab_report', 'discharge_summary', 'doctor_notes', 'other'].map((type) => (
          <button
            key={type}
            onClick={() => setDocType(type)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              docType === type
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'bg-white/5 text-gray-400 border border-white/5 hover:border-white/10'
            }`}
          >
            {type.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Message */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`p-3 rounded-xl text-sm ${
              message.type === 'success'
                ? 'bg-green-500/10 border border-green-500/20 text-green-400'
                : 'bg-red-500/10 border border-red-500/20 text-red-400'
            }`}
          >
            {message.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Documents List */}
      {documents.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-white font-semibold text-sm">Your Documents ({documents.length})</h3>
          {documents.map((doc) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between p-4 bg-white/[0.03] border border-white/[0.06] rounded-xl"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="text-lg">
                  {doc.mime_type?.includes('pdf') ? '📄' : '🖼️'}
                </span>
                <div className="min-w-0">
                  <p className="text-white text-sm font-medium truncate">{doc.original_filename}</p>
                  <p className="text-gray-500 text-xs">
                    {doc.doc_type.replace('_', ' ')} • {formatSize(doc.file_size_bytes)} • {doc.ocr_status}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => handleDownload(doc.id)}
                  className="px-3 py-1.5 text-xs text-blue-400 border border-blue-500/20 rounded-lg hover:bg-blue-500/10 transition-all"
                >
                  Download
                </button>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="px-3 py-1.5 text-xs text-red-400 border border-red-500/20 rounded-lg hover:bg-red-500/10 transition-all"
                >
                  Delete
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
