import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowUpDown, Search, Trash2, X } from 'lucide-react'

import {
  deleteAnalysis,
  fetchAnalysis,
  fetchAnalysisHistory,
  getApiErrorMessage,
} from '../services/api/analysis'
import type { AnalysisDetail, AnalysisSessionSummary, AnalysisSort, AnalysisStatus } from '../types/analysis'

const STATUS_FILTERS: Array<{ value: AnalysisStatus | ''; label: string }> = [
  { value: '', label: 'All statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'processing', label: 'Processing' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
]

const PAGE_SIZE = 10

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function StatusBadge({ status }: { status: AnalysisStatus }) {
  const tone =
    status === 'completed'
      ? { dot: 'bg-lime', text: 'text-lime' }
      : status === 'failed'
        ? { dot: 'bg-[#B45454]', text: 'text-[#FF8A8A]' }
        : { dot: 'bg-[#8E8E8A] beam-pulse', text: 'text-mist' }

  return (
    <span className={`inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider ${tone.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${tone.dot}`} aria-hidden="true" />
      {status}
    </span>
  )
}

export function HistoryPage() {
  const queryClient = useQueryClient()

  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<AnalysisStatus | ''>('')
  const [sort, setSort] = useState<AnalysisSort>('created_desc')
  const [page, setPage] = useState(1)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  // Debounce search input into an actual query parameter.
  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearch(searchInput.trim())
      setPage(1)
    }, 350)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  const historyQuery = useQuery({
    queryKey: ['analysis-history', search, statusFilter, sort, page],
    queryFn: () =>
      fetchAnalysisHistory({
        page,
        page_size: PAGE_SIZE,
        search: search || undefined,
        status: statusFilter || undefined,
        sort,
      }),
  })

  const deleteMutation = useMutation({
    mutationFn: (sessionId: string) => deleteAnalysis(sessionId),
    onSuccess: async (_data, sessionId) => {
      setSelectedId((current) => (current === sessionId ? null : current))
      await queryClient.invalidateQueries({ queryKey: ['analysis-history'] })
    },
    onError: (error) => setActionError(getApiErrorMessage(error)),
  })

  const detailQuery = useQuery({
    queryKey: ['analysis-detail', selectedId],
    queryFn: () => fetchAnalysis(selectedId as string),
    enabled: selectedId !== null,
    staleTime: Infinity,
  })

  const items = useMemo(() => historyQuery.data?.items ?? [], [historyQuery.data])
  const totalPages = historyQuery.data?.pages ?? 1

  const toggleSort = () => {
    setSort((current) => (current === 'created_desc' ? 'created_asc' : 'created_desc'))
    setPage(1)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Header */}
      <header className="flex flex-col justify-between gap-4 border-b border-line-subtle pb-5 sm:flex-row sm:items-end">
        <div className="space-y-1">
          <span className="text-[10px] font-medium uppercase tracking-[0.22em] text-lime">
            WORKSPACE // LOG ARCHIVE
          </span>
          <h1 className="font-display text-3xl font-semibold tracking-wide text-chalk sm:text-4xl">
            Analysis History
          </h1>
          <p className="text-xs text-dim sm:text-sm">
            Browse and inspect your past analysis sessions.
          </p>
        </div>
        <Link to="/analysis" className="kc kc--primary px-4 py-2 text-xs font-ui font-semibold uppercase tracking-[0.06em] w-fit">
          New analysis →
        </Link>
      </header>

      {/* Controls */}
      <div className="flex flex-col items-center gap-3 sm:flex-row">
        <div className="relative w-full flex-1">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-dim" aria-hidden="true" />
          <input
            type="search"
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Search by title or text content..."
            aria-label="Search analysis history"
            className="kc-input py-2 pl-9 text-xs"
          />
        </div>

        <label className="flex w-full items-center gap-2 sm:w-auto">
          <span className="sr-only">Filter by status</span>
          <select
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value as AnalysisStatus | '')
              setPage(1)
            }}
            aria-label="Filter by status"
            className="kc-input w-full cursor-pointer py-2 text-xs sm:w-40"
          >
            {STATUS_FILTERS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          onClick={toggleSort}
          className="kc px-3.5 py-2 text-xs font-ui font-medium uppercase tracking-[0.06em]"
          aria-label={`Sort by date ${sort === 'created_desc' ? 'newest first' : 'oldest first'}`}
        >
          <ArrowUpDown className="h-3.5 w-3.5" aria-hidden="true" />
          {sort === 'created_desc' ? 'Newest' : 'Oldest'}
        </button>
      </div>

      {actionError ? (
        <div role="alert" className="flex items-center justify-between gap-4 rounded-module border border-[#4A1A1A] bg-[#160D0D] p-4">
          <p className="text-xs text-[#FF8A8A]">{actionError}</p>
          <button
            type="button"
            onClick={() => setActionError(null)}
            className="kc kc--ghost px-3 py-1.5 text-xs uppercase"
          >
            Dismiss
          </button>
        </div>
      ) : null}

      {/* Table */}
      <section className="kc-card overflow-hidden" aria-label="Analysis sessions" aria-busy={historyQuery.isPending}>
        {historyQuery.isPending ? (
          <div className="space-y-3 p-5" role="status" aria-label="Loading history">
            {[0, 1, 2].map((row) => (
              <div key={row} className="h-10 animate-pulse rounded-keycap bg-raised" style={{ opacity: 1 - row * 0.25 }} />
            ))}
          </div>
        ) : historyQuery.isError ? (
          <div role="alert" className="flex flex-col items-start gap-3 p-6">
            <p className="text-sm text-[#FF8A8A]">{getApiErrorMessage(historyQuery.error)}</p>
            <button
              type="button"
              onClick={() => historyQuery.refetch()}
              className="kc px-4 py-2 text-xs font-ui font-medium uppercase tracking-[0.06em]"
            >
              Retry
            </button>
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-3 p-12 text-center">
            <p className="font-display text-base font-semibold uppercase tracking-[0.08em] text-chalk">
              No analysis sessions found
            </p>
            <p className="max-w-sm text-xs leading-relaxed text-dim">
              {search || statusFilter
                ? 'No sessions match the current filters. Adjust the search or filter and try again.'
                : 'Run your first analysis from the Analyze workspace and it will appear here.'}
            </p>
            <Link to="/analysis" className="kc kc--primary mt-2 px-4 py-2 text-xs font-ui font-semibold uppercase tracking-[0.06em]">
              Open Analyze
            </Link>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-ui">
                <caption className="sr-only">Your analysis sessions</caption>
                <thead className="border-b border-line-subtle bg-deep text-[10px] font-medium uppercase tracking-[0.16em] text-dim">
                  <tr>
                    <th scope="col" className="px-4 py-3">Session</th>
                    <th scope="col" className="px-4 py-3">Source</th>
                    <th scope="col" className="px-4 py-3">Primary emotion</th>
                    <th scope="col" className="px-4 py-3">Confidence</th>
                    <th scope="col" className="px-4 py-3">Created</th>
                    <th scope="col" className="px-4 py-3">Status</th>
                    <th scope="col" className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line-subtle">
                  {items.map((record) => (
                    <HistoryRow
                      key={record.session_id}
                      record={record}
                      onInspect={() => setSelectedId(record.session_id)}
                      onDelete={() => {
                        if (window.confirm('Delete this analysis session permanently?')) {
                          deleteMutation.mutate(record.session_id)
                        }
                      }}
                      deletePending={deleteMutation.isPending && deleteMutation.variables === record.session_id}
                    />
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <nav
              aria-label="History pagination"
              className="flex flex-wrap items-center justify-between gap-3 border-t border-line-subtle bg-deep px-4 py-3 text-[11px] text-dim"
            >
              <span>
                Page {historyQuery.data?.page ?? 1} of {totalPages} ·{' '}
                {historyQuery.data?.total ?? 0} session{(historyQuery.data?.total ?? 0) === 1 ? '' : 's'}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  className="kc px-3 py-1.5 text-[11px] font-medium uppercase"
                >
                  ← Prev
                </button>
                <button
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() => setPage((current) => current + 1)}
                  className="kc px-3 py-1.5 text-[11px] font-medium uppercase"
                >
                  Next →
                </button>
              </div>
            </nav>
          </>
        )}
      </section>

      {/* Detail dialog */}
      {selectedId ? (
        <DetailsDialog
          onClose={() => setSelectedId(null)}
          detail={detailQuery.data ?? null}
          isLoading={detailQuery.isPending}
          error={detailQuery.isError ? getApiErrorMessage(detailQuery.error) : null}
        />
      ) : null}
    </div>
  )
}

function HistoryRow({
  record,
  onInspect,
  onDelete,
  deletePending,
}: {
  record: AnalysisSessionSummary
  onInspect: () => void
  onDelete: () => void
  deletePending: boolean
}) {
  return (
    <tr className="group transition-colors duration-150 hover:bg-raised/60">
      <td className="max-w-[280px] px-4 py-3.5">
        <button
          type="button"
          onClick={onInspect}
          className="block max-w-full truncate text-left font-medium text-chalk group-hover:text-white"
          title={record.title ?? 'Untitled session'}
        >
          {record.title ?? 'Untitled session'}
        </button>
        <span className="mt-0.5 block font-mono text-[10px] text-dim">
          {record.session_id.slice(0, 8)}…
        </span>
      </td>
      <td className="px-4 py-3.5 text-mist">{record.source_type}</td>
      <td className="px-4 py-3.5 font-mono text-lime">
        {record.primary_emotion ?? <span className="text-dim">pending model</span>}
      </td>
      <td className="px-4 py-3.5 font-mono text-chalk">
        {record.confidence != null ? `${(record.confidence * 100).toFixed(1)}%` : '—'}
      </td>
      <td className="whitespace-nowrap px-4 py-3.5 font-mono text-dim">
        {formatDateTime(record.created_at)}
      </td>
      <td className="px-4 py-3.5">
        <StatusBadge status={record.status} />
      </td>
      <td className="px-4 py-3.5">
        <div className="flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onInspect}
            className="kc kc--ghost px-2.5 py-1 text-[11px] font-medium uppercase"
          >
            Inspect
          </button>
          <button
            type="button"
            onClick={onDelete}
            disabled={deletePending}
            aria-label={`Delete session ${record.title ?? record.session_id.slice(0, 8)}`}
            className="kc kc--ghost px-2 py-1 text-[#B8B8B0] hover:text-[#FF8A8A]"
          >
            <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>
      </td>
    </tr>
  )
}

function DetailsDialog({
  detail,
  isLoading,
  error,
  onClose,
}: {
  detail: AnalysisDetail | null
  isLoading: boolean
  error: string | null
  onClose: () => void
}) {
  // Close on Escape.
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKeyDown)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = ''
    }
  }, [onClose])

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Analysis session details"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <button
        type="button"
        aria-label="Close details"
        onClick={onClose}
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
      />
      <div className="kc-panel relative z-10 max-h-[85vh] w-full max-w-xl overflow-y-auto p-6 shadow-keycap-hover">
        <div className="mb-4 flex items-center justify-between border-b border-line-subtle pb-3">
          <h2 className="font-display text-lg font-semibold uppercase tracking-wide text-chalk">
            Session Details
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="kc kc--ghost h-8 w-8"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        {isLoading ? (
          <p role="status" className="py-8 text-center text-xs uppercase tracking-widest text-dim">
            Loading session…
          </p>
        ) : error ? (
          <p role="alert" className="py-6 text-sm text-[#FF8A8A]">{error}</p>
        ) : detail ? (
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <InfoTile label="Status">
                <StatusBadge status={detail.status} />
              </InfoTile>
              <InfoTile label="Primary emotion">
                {detail.primary_emotion ?? <span className="text-dim">pending model</span>}
              </InfoTile>
              <InfoTile label="Confidence">
                {detail.confidence != null ? `${(detail.confidence * 100).toFixed(1)}%` : '—'}
              </InfoTile>
              <InfoTile label="Source type">{detail.source_type}</InfoTile>
              <InfoTile label="Created">{formatDateTime(detail.created_at)}</InfoTile>
              <InfoTile label="Model">
                {detail.model_info.model_name ?? '—'} · {detail.model_info.deployed ? 'deployed' : 'not deployed'}
              </InfoTile>
            </div>

            <div>
              <p className="mb-1.5 text-[10px] font-medium uppercase tracking-[0.18em] text-dim">
                Analyzed text · {detail.input.word_count.toLocaleString()} words
              </p>
              <p className="rounded-keycap border border-line-subtle bg-deep p-3.5 leading-relaxed text-chalk shadow-well">
                “{detail.input.raw_text}”
              </p>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}

function InfoTile({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="rounded-keycap border border-line-subtle bg-surface p-3">
      <p className="text-[9px] font-medium uppercase tracking-[0.16em] text-dim">{label}</p>
      <div className="mt-1 truncate font-mono text-xs text-chalk">{children}</div>
    </div>
  )
}
