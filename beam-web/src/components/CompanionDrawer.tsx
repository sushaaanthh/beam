import { useState, useEffect, useRef } from 'react'
import {
  MessageSquare,
  X,
  Send,
  Sparkles,
  Trash2,
  Activity,
  HeartHandshake,
  Bot,
  User,
  Brain,
  ChevronDown,
  Info,
} from 'lucide-react'
import { beamApi, ChatMessage } from '../services/api/beam'

interface CompanionDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export function CompanionDrawer({ isOpen, onClose }: CompanionDrawerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [dailySummary, setDailySummary] = useState<string | null>(null)
  const [showSummary, setShowSummary] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      loadHistory()
      loadSummary()
    }
  }, [isOpen])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadSummary = async () => {
    try {
      const res = await beamApi.getChatSummary()
      if (res.data?.summary) {
        setDailySummary(res.data.summary)
      }
    } catch {
      // Ignore
    }
  }

  const loadHistory = async () => {
    try {
      const res = await beamApi.getChatHistory()
      if (res.data && res.data.length > 0) {
        setMessages(res.data)
      } else {
        setMessages([
          {
            id: 'INIT-1',
            sender: 'companion',
            message:
              "Hello! I'm your BEAM AI Companion. Whether you want to reflect on a challenging sprint, celebrate a milestone, or unpack emotional friction, I'm here to listen.",
            detected_emotion: 'Empathetic Support',
            confidence: 98,
            created_at: new Date().toISOString(),
          },
        ])
      }
    } catch {
      setMessages([
        {
          id: 'INIT-1',
          sender: 'companion',
          message:
            "Hello! I'm your BEAM AI Companion. Whether you want to reflect on a challenging sprint, celebrate a milestone, or unpack emotional friction, I'm here to listen.",
          detected_emotion: 'Empathetic Support',
          confidence: 98,
          created_at: new Date().toISOString(),
        },
      ])
    }
  }

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!input.trim() || loading) return

    const userText = input.trim()
    setInput('')
    setLoading(true)

    // Optimistic user bubble
    const tempUserMsg: ChatMessage = {
      id: `TMP-${Date.now()}`,
      sender: 'user',
      message: userText,
      detected_emotion: 'Analyzing...',
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUserMsg])

    try {
      const res = await beamApi.sendChatMessage(userText)
      if (res.history) {
        setMessages(res.history)
      }
      loadSummary()
    } catch {
      // Offline fallback
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: `FALLBACK-${Date.now()}`,
            sender: 'companion',
            message:
              "Thank you for sharing your reflection. Diving into challenges with structured awareness is how long-term psychological resilience is built.",
            detected_emotion: 'Empathetic Support',
            confidence: 96,
            created_at: new Date().toISOString(),
          },
        ])
      }, 500)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = async () => {
    try {
      await beamApi.clearChatHistory()
      setMessages([])
      setDailySummary(null)
    } catch {
      setMessages([])
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-[#080808] border-l border-[#1F1F1F] shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-4 border-b border-[#1C1C1C] bg-[#0C0C0C] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-[#C7FF4A]/10 border border-[#C7FF4A]/30 flex items-center justify-center text-[#C7FF4A]">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-[#F5F5F0] flex items-center gap-1.5">
              BEAM AI Companion
              <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A] animate-pulse" />
            </h3>
            <p className="text-[10px] text-[#73736F] font-mono">Contextual Journal Memory & Telemetry Active</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={handleClear}
            className="p-1.5 text-[#73736F] hover:text-[#FF6B6B] hover:bg-[#181818] rounded-md transition-colors"
            title="Clear conversation"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-[#73736F] hover:text-white hover:bg-[#181818] rounded-md transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Daily Trajectory Summary Banner */}
      {dailySummary && (
        <div className="px-4 py-2.5 bg-[#121212] border-b border-[#1C1C1C] flex items-start gap-2 text-[11px] text-[#B8B8B0]">
          <Sparkles className="h-3.5 w-3.5 text-[#C7FF4A] shrink-0 mt-0.5" />
          <p className="leading-snug">
            <strong className="text-[#C7FF4A] font-mono uppercase text-[10px] block">Daily Trajectory Summary</strong>
            {dailySummary}
          </p>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => {
          const isUser = m.sender === 'user'
          return (
            <div key={m.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
              <div
                className={`max-w-[85%] rounded-xl p-3.5 text-xs leading-relaxed ${
                  isUser
                    ? 'bg-[#181818] border border-[#2A2A2A] text-[#F5F5F0] rounded-br-sm'
                    : 'bg-[#0E0E0E] border border-[#1E1E1E] text-[#D4D4CE] rounded-bl-sm shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]'
                }`}
              >
                <p>{m.message}</p>

                {/* Emotion telemetry badge per message */}
                {m.detected_emotion && (
                  <div
                    className={`mt-2 pt-1.5 border-t border-[#222222] flex items-center justify-between text-[10px] font-mono ${
                      isUser ? 'text-[#C7FF4A]' : 'text-[#73736F]'
                    }`}
                  >
                    <span className="flex items-center gap-1 font-semibold">
                      <Activity className="h-2.5 w-2.5" /> {m.detected_emotion}
                    </span>
                    {m.confidence && <span>{m.confidence}%</span>}
                  </div>
                )}

                {/* Trigger word chips */}
                {m.trigger_words && m.trigger_words.length > 0 && isUser && (
                  <div className="flex flex-wrap gap-1 mt-1.5 pt-1 border-t border-[#222222]">
                    {m.trigger_words.map((tw) => (
                      <span
                        key={tw}
                        className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-[#222222] text-[#C7FF4A]"
                      >
                        #{tw}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {loading && (
          <div className="flex items-center gap-2 text-xs font-mono text-[#73736F]">
            <Sparkles className="h-3.5 w-3.5 text-[#C7FF4A] animate-spin" />
            Companion is formulating response...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-3 border-t border-[#1C1C1C] bg-[#0A0A0A]">
        <div className="flex items-center gap-2 bg-[#121212] border border-[#222222] rounded-xl px-3 py-1.5 focus-within:border-[#C7FF4A]">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Share what's on your mind... (e.g. 'I'm exhausted' or 'I solved it')"
            className="bg-transparent text-xs text-[#F5F5F0] placeholder:text-[#555552] focus:outline-none w-full py-1.5"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="h-7 w-7 rounded-lg bg-[#C7FF4A] text-[#080808] flex items-center justify-center disabled:opacity-30 transition-opacity shrink-0"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </div>
      </form>
    </div>
  )
}
