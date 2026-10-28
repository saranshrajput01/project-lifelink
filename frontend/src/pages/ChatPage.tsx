import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/services/api'

interface Msg {
  role: 'user' | 'assistant'
  content: string
}

const SUGGESTIONS = [
  'Explain my latest report',
  'What medications am I on?',
  'Summarize my health records',
  'Which of my lab values are abnormal?',
]

export function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: 'assistant',
      content:
        "Namaste 👋 I'm your LIFELINK health assistant. Ask me about your uploaded records, reports, or medications. I can't diagnose — always confirm with your doctor.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async (text: string) => {
    const msg = text.trim()
    if (!msg || loading) return
    const history = messages.filter((m) => m.role === 'user' || m.role === 'assistant')
    setMessages((m) => [...m, { role: 'user', content: msg }])
    setInput('')
    setLoading(true)
    try {
      const res = await api.post('/assistant/chat', { message: msg, history })
      setMessages((m) => [...m, { role: 'assistant', content: res.data.reply }])
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: '⚠️ Could not reach the assistant. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white flex flex-col">
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[128px]" />
      </div>

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
            <span className="text-white font-black text-base">L</span>
          </div>
          <span className="text-xl font-black bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
            LIFELINK
          </span>
        </div>
        <Link
          to="/dashboard"
          className="px-4 py-2 text-gray-400 hover:text-white font-medium transition-colors border border-white/5 rounded-xl hover:border-white/20 hover:bg-white/5"
        >
          Dashboard
        </Link>
      </nav>

      {/* Chat area */}
      <main className="relative z-10 flex-1 flex flex-col max-w-3xl w-full mx-auto px-4 py-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🤖</span>
          <h1 className="text-xl font-bold">AI Healthcare Assistant</h1>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pb-4">
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-br-sm'
                    : 'bg-white/[0.05] border border-white/10 text-gray-100 rounded-bl-sm'
                }`}
              >
                {m.content}
              </div>
            </motion.div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="px-4 py-3 rounded-2xl bg-white/[0.05] border border-white/10 text-gray-400 text-sm">
                Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="px-3 py-1.5 text-xs rounded-lg bg-white/5 border border-white/10 text-gray-300 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault()
            send(input)
          }}
          className="flex items-center gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your health records…"
            className="flex-1 px-4 py-3 bg-white/[0.05] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all"
          />
          <motion.button
            type="submit"
            disabled={loading || !input.trim()}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="px-5 py-3 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-xl text-sm font-semibold disabled:opacity-40 transition-all"
          >
            Send
          </motion.button>
        </form>
        <p className="text-center text-[11px] text-gray-600 mt-2">
          AI assistant — informational only, not a substitute for professional medical advice.
        </p>
      </main>
    </div>
  )
}
