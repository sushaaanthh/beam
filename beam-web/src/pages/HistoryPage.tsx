import { useState } from 'react'
import {
  Search,
  Filter,
  ArrowUpDown,
  Download,
  Eye,
  CheckCircle2,
  X,
  FileText,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

const historyRecords = [
  {
    id: 'AN-8921',
    title: 'Developer retrospective feedback #42',
    source: 'Dev Community Corpus',
    emotion: 'Joy / Fulfillment',
    confidence: '96.4%',
    model: 'RoBERTa-v1.2',
    created: '2026-08-17 16:30',
    status: 'COMPLETED',
    tokens: 420,
    text: "Refactored the entire telemetry pipeline into Rust. Latency dropped by 80% and the memory footprint is now virtually flat across high concurrency.",
  },
  {
    id: 'AN-8920',
    title: 'Quarterly architecture review notes',
    source: 'Technical Forum',
    emotion: 'Contemplation',
    confidence: '89.1%',
    model: 'RoBERTa-v1.2',
    created: '2026-08-17 14:15',
    status: 'COMPLETED',
    tokens: 680,
    text: "We need to carefully weigh the trade-offs between zero-copy deserialization and backward schema compatibility for our distributed data nodes.",
  },
  {
    id: 'AN-8919',
    title: 'Bug report thread: memory allocation crash',
    source: 'Issue Tracker',
    emotion: 'Frustration / Concern',
    confidence: '92.7%',
    model: 'RoBERTa-v1.2',
    created: '2026-08-17 11:04',
    status: 'COMPLETED',
    tokens: 215,
    text: "Every second release introduces a regression in the allocation pool. It is taking hours to diagnose memory leaks that should have been caught in CI.",
  },
  {
    id: 'AN-8918',
    title: 'Open source release announcement discussion',
    source: 'Reddit Feed',
    emotion: 'Excitement',
    confidence: '94.0%',
    model: 'BERT-Base',
    created: '2026-08-16 21:40',
    status: 'COMPLETED',
    tokens: 530,
    text: "Super thrilled to announce B.E.A.M. v1.0 public release! Looking forward to community contributions and benchmark feedback.",
  },
  {
    id: 'AN-8917',
    title: 'Code review discussion on PR #104',
    source: 'GitHub Discussions',
    emotion: 'Neutral / Analytical',
    confidence: '91.2%',
    model: 'RoBERTa-v1.2',
    created: '2026-08-16 18:22',
    status: 'COMPLETED',
    tokens: 310,
    text: "Please verify that the mutex lock is released before returning in the error propagation branch on line 142.",
  },
]

export function HistoryPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRecord, setSelectedRecord] = useState<typeof historyRecords[0] | null>(null)

  const filteredRecords = historyRecords.filter(
    (r) =>
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.emotion.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.id.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-4">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            WORKSPACE // LOG ARCHIVE
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            ANALYSIS HISTORY
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Browse, inspect, and export past behavioral emotion inference executions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="secondary" size="sm" leftIcon={<Download className="h-3.5 w-3.5" />}>
            Export CSV
          </Button>
        </div>
      </div>

      {/* Search & Filter Bar */}
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

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Button variant="secondary" size="sm" leftIcon={<Filter className="h-3.5 w-3.5" />}>
            Filter
          </Button>
          <Button variant="secondary" size="sm" leftIcon={<ArrowUpDown className="h-3.5 w-3.5" />}>
            Sort: Date
          </Button>
        </div>
      </div>

      {/* History Table */}
      <Card variant="default" padding="none" className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-ui">
            <thead className="bg-[#0A0A0A] border-b border-[#1C1C1C] text-[10px] font-mono text-[#73736F] uppercase">
              <tr>
                <th className="py-3 px-4">Analysis</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Predicted Emotion</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Model</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#181818]">
              {filteredRecords.map((rec) => (
                <tr
                  key={rec.id}
                  onClick={() => setSelectedRecord(rec)}
                  className="hover:bg-[#121212] transition-colors cursor-pointer group"
                >
                  <td className="py-3.5 px-4">
                    <span className="font-mono text-[10px] text-[#73736F] mr-2 bg-[#141414] px-1.5 py-0.5 rounded border border-[#222222]">
                      {rec.id}
                    </span>
                    <span className="font-medium text-[#F5F5F0] group-hover:text-white">
                      {rec.title}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-[#B8B8B0]">{rec.source}</td>
                  <td className="py-3.5 px-4 font-mono font-medium text-[#C7FF4A]">
                    {rec.emotion}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[#F5F5F0]">{rec.confidence}</td>
                  <td className="py-3.5 px-4 font-mono text-[#73736F]">{rec.model}</td>
                  <td className="py-3.5 px-4 text-[#73736F] font-mono">{rec.created}</td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center gap-1 font-mono text-[10px] text-[#C7FF4A]">
                      <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A]" />
                      {rec.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <Button variant="ghost" size="sm" className="px-2 py-1 text-[11px]">
                      Inspect
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Details Modal / Glass Dialog */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="relative w-full max-w-xl rounded-2xl bg-[#0E0E0E] border border-[#2A2A2A] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_20px_50px_rgba(0,0,0,0.9)] space-y-5">
            <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-[#C7FF4A] bg-[#141414] px-2 py-1 rounded border border-[#262626]">
                  {selectedRecord.id}
                </span>
                <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
                  INSPECTION DETAILS
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
                <span className="text-[10px] font-mono text-[#73736F] uppercase">Analyzed Text Sample</span>
                <p className="mt-1 p-3.5 rounded-lg bg-[#080808] border border-[#1E1E1E] text-xs text-[#F5F5F0] leading-relaxed">
                  "{selectedRecord.text}"
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Predicted Emotion</span>
                  <span className="font-display text-lg font-bold text-[#C7FF4A] block mt-0.5">
                    {selectedRecord.emotion}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Model Confidence</span>
                  <span className="font-display text-lg font-bold text-[#F5F5F0] block mt-0.5">
                    {selectedRecord.confidence}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Transformer Model</span>
                  <span className="font-mono text-xs text-[#B8B8B0] block mt-0.5">
                    {selectedRecord.model}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-[#121212] border border-[#222222]">
                  <span className="text-[10px] text-[#73736F] font-mono uppercase block">Source Corpus</span>
                  <span className="text-xs text-[#B8B8B0] block mt-0.5">
                    {selectedRecord.source}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-[#1C1C1C] flex justify-end gap-3">
              <Button variant="secondary" size="sm" onClick={() => setSelectedRecord(null)}>
                Close
              </Button>
              <Button variant="primary" size="sm" rightIcon={<FileText className="h-3.5 w-3.5" />}>
                Export Report
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}