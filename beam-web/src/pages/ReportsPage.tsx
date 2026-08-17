import { useState } from 'react'
import {
  FileText,
  Download,
  Eye,
  Plus,
  Search,
  CheckCircle2,
  Calendar,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

const reports = [
  {
    id: 'REP-2026-08',
    title: 'Developer Sentiment & Affective Trends Report',
    analysis: 'Dev Community Corpus (58k records)',
    generated: '2026-08-17 12:00',
    model: 'RoBERTa-v1.2',
    status: 'READY',
    format: 'PDF (2.4 MB)',
  },
  {
    id: 'REP-2026-07',
    title: 'Quarterly Transformer Benchmark & Saliency Audit',
    analysis: 'GoEmotions Benchmark Split',
    generated: '2026-08-01 09:30',
    model: 'DeBERTa-v3',
    status: 'READY',
    format: 'PDF (4.1 MB)',
  },
  {
    id: 'REP-2026-06',
    title: 'Behavioral Signal Transition Evaluation',
    analysis: 'Retrospective Ingestion Batch',
    generated: '2026-07-15 17:45',
    model: 'BERT-Base',
    status: 'READY',
    format: 'CSV + PDF',
  },
]

export function ReportsPage() {
  const [search, setSearch] = useState('')

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-4">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            WORKSPACE // EXPORTED SYNTHESIS
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            REPORTS
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Generated academic synthesis summaries, attribution reports, and telemetry exports.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="primary" size="sm" leftIcon={<Plus className="h-3.5 w-3.5" />}>
            GENERATE REPORT
          </Button>
        </div>
      </div>

      <Card variant="default" padding="none" className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-ui">
            <thead className="bg-[#0A0A0A] border-b border-[#1C1C1C] text-[10px] font-mono text-[#73736F] uppercase">
              <tr>
                <th className="py-3 px-4">Report Title</th>
                <th className="py-3 px-4">Corpus / Analysis</th>
                <th className="py-3 px-4">Generated</th>
                <th className="py-3 px-4">Model</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#181818]">
              {reports.map((rep) => (
                <tr key={rep.id} className="hover:bg-[#121212] transition-colors">
                  <td className="py-3.5 px-4 font-medium text-[#F5F5F0]">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-[#C7FF4A] shrink-0" />
                      <span>{rep.title}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-[#B8B8B0]">{rep.analysis}</td>
                  <td className="py-3.5 px-4 text-[#73736F] font-mono">{rep.generated}</td>
                  <td className="py-3.5 px-4 font-mono text-[#73736F]">{rep.model}</td>
                  <td className="py-3.5 px-4 font-mono text-[#73736F]">{rep.format}</td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center gap-1 font-mono text-[10px] text-[#C7FF4A]">
                      <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A]" />
                      {rep.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button variant="ghost" size="sm" className="px-2 py-1 text-[11px]" leftIcon={<Eye className="h-3 w-3" />}>
                        View
                      </Button>
                      <Button variant="secondary" size="sm" className="px-2 py-1 text-[11px]" leftIcon={<Download className="h-3 w-3" />}>
                        Download
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
