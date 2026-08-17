import { useState } from 'react'
import {
  Database,
  Plus,
  Download,
  Filter,
  Search,
  ExternalLink,
  RefreshCw,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

const datasets = [
  {
    id: 'DS-01',
    name: 'GoEmotions Benchmark Corpus',
    source: 'Reddit Curated Feed',
    samples: '58,009',
    labels: '28 Fine-grained',
    version: 'v2.1',
    status: 'ACTIVE',
    updated: '2026-08-10',
  },
  {
    id: 'DS-02',
    name: 'Developer Affective Telemetry',
    source: 'Dev Community & Forum',
    samples: '14,240',
    labels: '6 Valence/Arousal',
    version: 'v1.4',
    status: 'ACTIVE',
    updated: '2026-08-14',
  },
  {
    id: 'DS-03',
    name: 'Technical Retrospective Corpus',
    source: 'Engineering Logs',
    samples: '8,920',
    labels: '12 Behavioral',
    version: 'v1.0',
    status: 'SYNCING',
    updated: '2026-08-17',
  },
  {
    id: 'DS-04',
    name: 'EmpatheticDialogues Split',
    source: 'Academic Benchmark',
    samples: '24,850',
    labels: '32 Emotional',
    version: 'v3.0',
    status: 'ACTIVE',
    updated: '2026-07-28',
  },
]

export function DatasetsPage() {
  const [search, setSearch] = useState('')

  const filtered = datasets.filter((d) =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.source.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-4">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            WORKSPACE // DATA REPOSITORY
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            DATASETS
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Manage behavioral training corpora, fine-tuning annotations, and streaming data feeds.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="primary" size="sm" leftIcon={<Plus className="h-3.5 w-3.5" />}>
            IMPORT DATASET
          </Button>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#555552]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search datasets by title or source..."
            className="w-full rounded-lg bg-[#0C0C0C] border border-[#222222] pl-9 pr-4 py-2 text-xs text-[#F5F5F0] font-ui placeholder:text-[#555552] focus:border-[#C7FF4A] focus:outline-none"
          />
        </div>
        <Button variant="secondary" size="sm" leftIcon={<Filter className="h-3.5 w-3.5" />}>
          Filter
        </Button>
      </div>

      {/* Datasets Table */}
      <Card variant="default" padding="none" className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-ui">
            <thead className="bg-[#0A0A0A] border-b border-[#1C1C1C] text-[10px] font-mono text-[#73736F] uppercase">
              <tr>
                <th className="py-3 px-4">Dataset Name</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Samples</th>
                <th className="py-3 px-4">Labels</th>
                <th className="py-3 px-4">Version</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Last Updated</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#181818]">
              {filtered.map((ds) => (
                <tr key={ds.id} className="hover:bg-[#121212] transition-colors">
                  <td className="py-3.5 px-4 font-medium text-[#F5F5F0]">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] text-[#73736F] bg-[#141414] px-1.5 py-0.5 rounded border border-[#222222]">
                        {ds.id}
                      </span>
                      <span>{ds.name}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-[#B8B8B0]">{ds.source}</td>
                  <td className="py-3.5 px-4 font-mono text-[#F5F5F0]">{ds.samples}</td>
                  <td className="py-3.5 px-4 text-[#73736F]">{ds.labels}</td>
                  <td className="py-3.5 px-4 font-mono text-[#73736F]">{ds.version}</td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-flex items-center gap-1 font-mono text-[10px] ${
                        ds.status === 'ACTIVE' ? 'text-[#C7FF4A]' : 'text-[#E5A93C]'
                      }`}
                    >
                      <span
                        className={`h-1.5 w-1.5 rounded-full ${
                          ds.status === 'ACTIVE' ? 'bg-[#C7FF4A]' : 'bg-[#E5A93C]'
                        }`}
                      />
                      {ds.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[#73736F]">{ds.updated}</td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button variant="ghost" size="sm" className="px-2 py-1 text-[11px]">
                        Inspect
                      </Button>
                      <Button variant="ghost" size="sm" className="px-2 py-1 text-[11px]">
                        Sync
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
