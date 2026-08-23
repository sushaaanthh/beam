import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import {
  Search,
  Filter,
  ArrowUpDown,
  Download,
  Eye,
  CheckCircle2,
  X,
  FileText,
  Plus,
  Brain,
  Trash2,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Layers,
  ArrowRight,
  TrendingUp,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { beamApi, JournalEntry } from '../services/api/beam'

export function HistoryPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [records, setRecords] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRecord, setSelectedRecord] = useState<JournalEntry | null>(null)

  // Replay Modal State
  const [replayOpen, setReplayOpen] = useState(false)
  const [replayIndex, setReplayIndex] = useState(0)
  const [isReplaying, setIsReplaying] = useState(false)
  const [replaySpeed, setReplaySpeed] = useState<1 | 2>(1)
  const replayIntervalRef = useRef<any>(null)

  // Compare Mode State
  const [compareMode, setCompareMode] = useState(false)
  const [compareSelectedIds, setCompareSelectedIds] = useState<string[]>([])

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const res = await beamApi.getJournals()
      if (res && res.data && res.data.length > 0) {
        setRecords(res.data)
      } else {
        setRecords([])
      }
    } catch {
      setRecords([])
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await beamApi.deleteJournal(id)
      setRecords((prev) => prev.filter((r) => r.id !== id))
      if (selectedRecord?.id === id) {
        setSelectedRecord(null)
      }
    } catch (err) {
      console.error(err)
    }
  }

  // AI Emotion Timeline Replay Handlers
  const startReplay = () => {
    if (records.length === 0) return
    setReplayOpen(true)
    setReplayIndex(0)
    setIsReplaying(true)
  }

  useEffect(() => {
    if (isReplaying && replayOpen) {
      clearInterval(replayIntervalRef.current)
      replayIntervalRef.current = setInterval(() => {
        setReplayIndex((prev) => {
          if (prev >= records.length - 1) {
            setIsReplaying(false)
            return prev
          }
          return prev + 1
        })
      }, 2500 / replaySpeed)
    } else {
      clearInterval(replayIntervalRef.current)
    }
    return () => clearInterval(replayIntervalRef.current)
  }, [isReplaying, replayOpen, replaySpeed, records.length])

  const toggleCompareSelect = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (compareSelectedIds.includes(id)) {
      setCompareSelectedIds((prev) => prev.filter((item) => item !== id))
    } else {
      if (compareSelectedIds.length >= 2) {
        setCompareSelectedIds([compareSelectedIds[1], id])
      } else {
        setCompareSelectedIds((prev) => [...prev, id])
      }
    }
  }

  const filteredRecords = records.filter(
    (r) =>
      r.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.primary_emotion.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.content.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const currentReplayEntry = records[replayIndex] || records[0]
  const comparedEntries = records.filter((r) => compareSelectedIds.includes(r.id))

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-4">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            WORKSPACE // LOG ARCHIVE & TIMELINE REPLAY
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            ANALYSIS HISTORY
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Browse, inspect, compare, and animate past behavioral emotion inference executions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {records.length > 0 && (
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setCompareMode(!compareMode)}
                className={compareMode ? 'border-[#C7FF4A] text-[#C7FF4A]' : ''}
              >
                {compareMode ? 'Exit Compare' : 'Compare 2 Entries'}
              </Button>

              <Button
                variant="secondary"
                size="sm"
                onClick={startReplay}
                leftIcon={<Play className="h-3.5 w-3.5 text-[#C7FF4A]" />}
              >
                Replay Timeline
              </Button>
            </>
          )}

          <Link to="/analysis">
            <Button variant="primary" size="sm" leftIcon={<Plus className="h-3.5 w-3.5" />}>
              NEW ENTRY
            </Button>
          </Link>
        </div>
      </div>

      {/* Compare Banner */}
      {compareMode && (
        <div className="p-4 rounded-xl bg-[#121212] border border-[#222222] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-[#B8B8B0]">
            <Layers className="h-4 w-4 text-[#C7FF4A]" />
            <span>Select 2 journal entries below to compare their SHAP token saliency and affective delta ({compareSelectedIds.length}/2 selected)</span>
          </div>
          {compareSelectedIds.length === 2 && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => setSelectedRecord(null)}
            >
              Comparing Selected
            </Button>
          )}
        </div>
      )}

      {/* Search & Filter Bar */}
      {records.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#555552]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by analysis ID, title, or predicted emotion..."
              className="w-full rounded-lg bg-[#0C0C0C] border border-[#222222] pl-9 pr-4 py-2 text-xs text-[#F5F5F0] font-ui placeholder:text-[#555552] focus:border-[#C7FF4A] focus:outline-none"
            />
          </div>
        </div>
      )}

      {/* History Content */}
      {loading ? (
        <div className="p-12 text-center text-xs font-mono text-[#73736F]">
          Loading analysis history...
        </div>
      ) : records.length === 0 ? (
        /* Empty State for New Accounts */
        <Card
          variant="default"
          padding="lg"
          className="p-12 flex flex-col items-center justify-center text-center border-dashed border-[#222222]"
        >
          <div className="h-12 w-12 rounded-xl bg-[#121212] border border-[#222222] flex items-center justify-center text-[#73736F] mb-4">
            <Brain className="h-6 w-6 text-[#C7FF4A]" />
          </div>
          <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
            NO ANALYSIS HISTORY RECORDED
          </h3>
          <p className="text-xs text-[#73736F] max-w-sm mt-1.5 leading-relaxed mb-6">
            This is a fresh account. Create your first daily reflection or record a voice note in the Affective Studio to begin building your emotional intelligence timeline.
          </p>
          <Link to="/analysis">
            <Button variant="primary" size="md" leftIcon={<Plus className="h-4 w-4" />}>
              Create First Reflection
            </Button>
          </Link>
        </Card>
      ) : (
        /* History Table */
        <Card variant="default" padding="none" className="overflow-hidden border-[#222222]">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-ui">
              <thead className="bg-[#0A0A0A] border-b border-[#1C1C1C] text-[10px] font-mono text-[#73736F] uppercase">
                <tr>
                  {compareMode && <th className="py-3 px-3 w-8">Select</th>}
                  <th className="py-3 px-4">Analysis / Entry</th>
                  <th className="py-3 px-4">Predicted Emotion</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Reflection Score</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#181818]">
                {filteredRecords.map((rec) => {
                  const isSelected = compareSelectedIds.includes(rec.id)
                  return (
                    <tr
                      key={rec.id}
                      onClick={() => setSelectedRecord(rec)}
                      className={`hover:bg-[#121212] transition-colors cursor-pointer group ${
                        isSelected ? 'bg-[#182412]' : ''
                      }`}
                    >
                      {compareMode && (
                        <td className="py-3.5 px-3">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => toggleCompareSelect(rec.id, e as any)}
                            className="accent-[#C7FF4A] h-4 w-4 rounded"
                          />
                        </td>
                      )}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] text-[#73736F] bg-[#141414] px-1.5 py-0.5 rounded border border-[#222222]">
                            {rec.id}
                          </span>
                          <span className="font-medium text-[#F5F5F0] group-hover:text-white">
                            {rec.title || 'Daily Journal'}
                          </span>
                          {rec.mood_emoji && <span>{rec.mood_emoji}</span>}
                        </div>
                        <p className="text-[11px] text-[#73736F] line-clamp-1 mt-0.5">
                          {rec.content}
                        </p>
                      </td>
                      <td className="py-3.5 px-4 font-mono font-medium text-[#C7FF4A]">
                        {rec.primary_emotion}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[#F5F5F0]">{rec.confidence}%</td>
                      <td className="py-3.5 px-4 font-mono text-[#B8B8B0]">{rec.reflection_score} / 100</td>
                      <td className="py-3.5 px-4 text-[#73736F] font-mono">
                        {rec.created_at ? new Date(rec.created_at).toLocaleString() : 'Just now'}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="sm" className="px-2 py-1 text-[11px]">
                            Inspect
                          </Button>
                          <button
                            type="button"
                            onClick={(e) => handleDelete(rec.id, e)}
                            className="p-1 text-[#73736F] hover:text-[#FF6B6B] hover:bg-[#180E0E] rounded transition-colors"
                            title="Delete entry"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Side-by-Side Comparison Modal */}
      {compareMode && comparedEntries.length === 2 && (
        <div className="p-6 rounded-2xl bg-[#0D0D0D] border border-[#242424] space-y-4">
          <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3">
            <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
              SIDE-BY-SIDE EMOTION COMPARISON
            </h3>
            <Button variant="secondary" size="sm" onClick={() => setCompareSelectedIds([])}>
              Clear Comparison
            </Button>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {comparedEntries.map((entry, idx) => (
              <div key={entry.id} className="p-4 rounded-xl bg-[#121212] border border-[#202020] space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-mono text-xs text-[#C7FF4A]">{entry.id} • {entry.title}</span>
                  <span className="font-mono text-[10px] text-[#73736F]">
                    {new Date(entry.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-xs text-[#D4D4CE] italic">"{entry.content}"</p>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-2 border-t border-[#1C1C1C]">
                  <div>
                    <span className="text-[#73736F] text-[10px] block">Emotion</span>
                    <strong className="text-[#C7FF4A]">{entry.primary_emotion}</strong>
                  </div>
                  <div>
                    <span className="text-[#73736F] text-[10px] block">Reflection</span>
                    <strong className="text-[#F5F5F0]">{entry.reflection_score}/100</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Killer Feature: AI Emotion Timeline Replay Modal */}
      {replayOpen && currentReplayEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl rounded-2xl bg-[#0C0C0C] border border-[#2A2A2A] p-6 shadow-2xl space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-[#C7FF4A] animate-pulse" />
                <h3 className="font-display text-xl font-bold text-[#F5F5F0]">
                  AI EMOTION TIMELINE REPLAY
                </h3>
              </div>
              <button
                type="button"
                onClick={() => {
                  setReplayOpen(false)
                  setIsReplaying(false)
                }}
                className="h-8 w-8 rounded-lg flex items-center justify-center text-[#73736F] hover:text-white hover:bg-[#1C1C1C]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Replay Stage Card */}
            <div className="p-6 rounded-2xl bg-[#141414] border border-[#242424] space-y-5 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-[#C7FF4A] bg-[#1E1E1E] px-2.5 py-1 rounded-lg border border-[#333333]">
                  ENTRY {replayIndex + 1} OF {records.length}
                </span>
                <span className="font-mono text-xs text-[#73736F]">
                  {new Date(currentReplayEntry.created_at).toLocaleDateString()}
                </span>
              </div>

              {/* Surfacing Text */}
              <div className="space-y-1.5">
                <h4 className="font-display text-lg font-bold text-[#F5F5F0]">
                  {currentReplayEntry.title} {currentReplayEntry.mood_emoji}
                </h4>
                <p className="text-sm text-[#D4D4CE] leading-relaxed p-4 rounded-xl bg-[#0A0A0A] border border-[#1E1E1E]">
                  "{currentReplayEntry.content}"
                </p>
              </div>

              {/* Dynamic Emotion Transition */}
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-3 rounded-xl bg-[#0C0C0C] border border-[#1E1E1E]">
                  <span className="text-[10px] text-[#73736F] font-mono block">Emotion State</span>
                  <span className="font-display text-base font-bold text-[#C7FF4A] block mt-0.5">
                    {currentReplayEntry.primary_emotion}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-[#0C0C0C] border border-[#1E1E1E]">
                  <span className="text-[10px] text-[#73736F] font-mono block">Confidence</span>
                  <span className="font-mono text-base font-bold text-[#F5F5F0] block mt-0.5">
                    {currentReplayEntry.confidence}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-[#0C0C0C] border border-[#1E1E1E]">
                  <span className="text-[10px] text-[#73736F] font-mono block">Wellness Index</span>
                  <span className="font-mono text-base font-bold text-[#C7FF4A] block mt-0.5">
                    {currentReplayEntry.reflection_score} / 100
                  </span>
                </div>
              </div>

              {/* Highlighting SHAP Trigger Keywords */}
              {currentReplayEntry.trigger_words && currentReplayEntry.trigger_words.length > 0 && (
                <div>
                  <span className="text-[10px] font-mono text-[#73736F] uppercase block mb-1.5">
                    Active SHAP Keywords
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {currentReplayEntry.trigger_words.map((kw) => (
                      <span
                        key={kw}
                        className="px-2 py-0.5 rounded text-xs font-mono bg-[#1E2E1E] border border-[#2E5E2E] text-[#C7FF4A] animate-bounce"
                      >
                        #{kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Replay Controls & Timeline Scrubber */}
            <div className="space-y-3 pt-2 border-t border-[#1C1C1C]">
              <input
                type="range"
                min={0}
                max={records.length - 1}
                value={replayIndex}
                onChange={(e) => {
                  setReplayIndex(Number(e.target.value))
                  setIsReplaying(false)
                }}
                className="w-full accent-[#C7FF4A] cursor-pointer"
              />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setIsReplaying(!isReplaying)}
                    leftIcon={isReplaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  >
                    {isReplaying ? 'Pause' : 'Play Timeline'}
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setReplayIndex(0)
                      setIsReplaying(true)
                    }}
                    leftIcon={<RotateCcw className="h-3.5 w-3.5" />}
                  >
                    Restart
                  </Button>
                </div>

                <div className="flex items-center gap-2 text-xs font-mono text-[#73736F]">
                  <span>Speed:</span>
                  <button
                    type="button"
                    onClick={() => setReplaySpeed(1)}
                    className={`px-2 py-1 rounded ${
                      replaySpeed === 1 ? 'bg-[#222222] text-[#C7FF4A] font-bold' : ''
                    }`}
                  >
                    1x
                  </button>
                  <button
                    type="button"
                    onClick={() => setReplaySpeed(2)}
                    className={`px-2 py-1 rounded ${
                      replaySpeed === 2 ? 'bg-[#222222] text-[#C7FF4A] font-bold' : ''
                    }`}
                  >
                    2x
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal / Glass Dialog */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="relative w-full max-w-xl rounded-2xl bg-[#0E0E0E] border border-[#2A2A2A] p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-[#C7FF4A] bg-[#141414] px-2 py-1 rounded border border-[#262626]">
                  {selectedRecord.id}
                </span>
                <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
                  {selectedRecord.title || 'INSPECTION DETAILS'}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRecord(null)}
                className="h-7 w-7 rounded-md flex items-center justify-center text-[#73736F] hover:text-white hover:bg-[#1C1C1C]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-[10px] font-mono text-[#73736F] uppercase">Analyzed Reflection Text</span>
                <p className="mt-1 p-3.5 rounded-lg bg-[#080808] border border-[#1E1E1E] text-xs text-[#F5F5F0] leading-relaxed">
                  "{selectedRecord.content}"
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Predicted Emotion</span>
                  <span className="font-display text-base font-bold text-[#C7FF4A] block mt-0.5">
                    {selectedRecord.primary_emotion}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Confidence</span>
                  <span className="font-display text-base font-bold text-[#F5F5F0] block mt-0.5">
                    {selectedRecord.confidence}%
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Reflection Depth</span>
                  <span className="font-mono text-sm font-bold text-[#C7FF4A] block mt-0.5">
                    {selectedRecord.reflection_score} / 100
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Model Pipeline</span>
                  <span className="font-mono text-xs text-[#B8B8B0] block mt-0.5">
                    RoBERTa-v1.2
                  </span>
                </div>
              </div>

              {/* Trigger Words */}
              {selectedRecord.trigger_words && selectedRecord.trigger_words.length > 0 && (
                <div>
                  <span className="text-[10px] font-mono text-[#73736F] uppercase block mb-1">
                    Highlighted Trigger Words
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedRecord.trigger_words.map((w) => (
                      <span
                        key={w}
                        className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#181818] border border-[#2A2A2A] text-[#C7FF4A]"
                      >
                        #{w}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-[#1C1C1C] flex justify-end gap-3">
              <Button variant="secondary" size="sm" onClick={() => setSelectedRecord(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}