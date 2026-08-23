import { useCallback, useEffect, useRef, useState, type ChangeEvent, type DragEvent } from 'react'
import { Eraser, Play, UploadCloud } from 'lucide-react'

import {
  ANALYSIS_POLL_INTERVAL_MS,
  ANALYSIS_POLL_TIMEOUT_MS,
  MAX_ANALYSIS_TEXT_CHARS,
  createAnalysis,
  fetchAnalysis,
  getApiErrorMessage,
} from '../services/api/analysis'
import type {
  AnalysisDetail,
  AnalysisStatus,
  SourceType,
} from '../types/analysis'
import { KeycapBadge } from '../components/keycap'
import { ProcessingSignal } from '../components/analysis/ProcessingSignal'
import { ResultWorkspace } from '../components/analysis/ResultWorkspace'

type WorkspaceState =
  | { phase: 'editing' }
  | { phase: 'processing'; sessionId: string }
  | { phase: 'result'; detail: AnalysisDetail }
  | { phase: 'error'; message: string }

const SOURCE_TYPES: Array<{ value: SourceType; label: string }> = [
  { value: 'text', label: 'Plain text' },
  { value: 'discussion', label: 'Discussion thread' },
  { value: 'social_feed', label: 'Social feed post' },
  { value: 'review', label: 'Review / comment' },
]

export function AnalysisPage() {
  const [text, setText] = useState('')
  const [sourceType, setSourceType] = useState<SourceType>('text')
  const [validationError, setValidationError] = useState<string | null>(null)
  const [state, setState] = useState<WorkspaceState>({ phase: 'editing' })
  const [fileName, setFileName] = useState<string | null>(null)

  const pollTimerRef = useRef<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(
    () => () => {
      if (pollTimerRef.current !== null) window.clearTimeout(pollTimerRef.current)
    },
    [],
  )

  const charCount = text.length
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  const overLimit = charCount > MAX_ANALYSIS_TEXT_CHARS

  const startPolling = useCallback((sessionId: string, startedAt: number) => {
    const poll = async () => {
      try {
        const detail = await fetchAnalysis(sessionId)
        const terminalStatuses: AnalysisStatus[] = ['completed', 'failed']
        if (terminalStatuses.includes(detail.status)) {
          if (detail.status === 'failed') {
            setState({ phase: 'error', message: 'The analysis failed while processing. Please try again.' })
            return
          }
          setState({ phase: 'result', detail })
          return
        }
        if (Date.now() - startedAt > ANALYSIS_POLL_TIMEOUT_MS) {
          setState({
            phase: 'error',
            message: 'Analysis is taking longer than expected. Check history later for its result.',
          })
          return
        }
        pollTimerRef.current = window.setTimeout(poll, ANALYSIS_POLL_INTERVAL_MS)
      } catch (error) {
        setState({ phase: 'error', message: getApiErrorMessage(error) })
      }
    }
    pollTimerRef.current = window.setTimeout(poll, ANALYSIS_POLL_INTERVAL_MS)
  }, [])

  const handleAnalyze = async () => {
    const trimmed = text.trim()
    if (!trimmed) {
      setValidationError('Enter or paste some text before starting an analysis.')
      textareaRef.current?.focus()
      return
    }
    if (overLimit) {
      setValidationError(`Text exceeds the maximum of ${MAX_ANALYSIS_TEXT_CHARS.toLocaleString()} characters.`)
      textareaRef.current?.focus()
      return
    }

    setValidationError(null)
    setState({ phase: 'processing', sessionId: '' })

    try {
      const created = await createAnalysis({ text: trimmed, source_type: sourceType })
      setState({ phase: 'processing', sessionId: created.session_id })

      // The placeholder service usually completes inside the POST itself;
      // polling covers pending/processing transitions from future async workers.
      if (created.status === 'pending' || created.status === 'processing') {
        startPolling(created.session_id, Date.now())
        return
      }

      const detail = await fetchAnalysis(created.session_id)
      if (detail.status === 'failed') {
        setState({ phase: 'error', message: 'The analysis failed while processing. Please try again.' })
        return
      }
      setState({ phase: 'result', detail })
    } catch (error) {
      setState({ phase: 'error', message: getApiErrorMessage(error) })
    }
  }

  const handleClear = () => {
    setText('')
    setValidationError(null)
    setFileName(null)
    setState({ phase: 'editing' })
    textareaRef.current?.focus()
  }

  const loadFile = async (file: File) => {
    if (!/\.(txt|md)$/i.test(file.name)) {
      setValidationError('Only plain-text files (.txt, .md) can be loaded.')
      return
    }
    try {
      const content = await file.text()
      if (content.length > MAX_ANALYSIS_TEXT_CHARS) {
        setValidationError(
          `"${file.name}" exceeds the maximum of ${MAX_ANALYSIS_TEXT_CHARS.toLocaleString()} characters.`,
        )
        return
      }
      setText(content.replace(/\r\n/g, '\n'))
      setFileName(file.name)
      setValidationError(null)
      setState({ phase: 'editing' })
    } catch {
      setValidationError('The file could not be read. Try a different plain-text file.')
    }
  }

  const handleFileSelected = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (file) await loadFile(file)
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files?.[0]
    if (file) void loadFile(file)
  }

  const resetToEditor = () => {
    setState({ phase: 'editing' })
    textareaRef.current?.focus()
  }

  const processing = state.phase === 'processing'

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {/* Header */}
      <header className="space-y-1 border-b border-line-subtle pb-5">
        <span className="text-[10px] font-medium uppercase tracking-[0.22em] text-lime">
          WORKSPACE // INFERENCE LAB
        </span>
        <h1 className="font-display text-3xl font-semibold tracking-wide text-chalk sm:text-4xl">
          Analyze
        </h1>
        <p className="text-xs text-dim sm:text-sm">
          Transform textual behavior into interpretable emotional insights.
        </p>
      </header>

      {state.phase === 'error' ? (
        <div
          role="alert"
          className="flex items-start justify-between gap-4 rounded-module border border-[#4A1A1A] bg-[#160D0D] p-4"
        >
          <div className="space-y-1">
            <p className="text-sm font-medium text-[#FF8A8A]">Analysis error</p>
            <p className="text-xs leading-relaxed text-mist">{state.message}</p>
          </div>
          <button
            type="button"
            onClick={resetToEditor}
            className="kc kc--ghost px-3 py-1.5 text-xs font-ui font-medium uppercase tracking-[0.06em]"
          >
            Dismiss
          </button>
        </div>
      ) : null}

      {state.phase === 'processing' ? (
        <section aria-busy="true" className="py-8">
          <ProcessingSignal sessionId={state.sessionId || undefined} />
        </section>
      ) : state.phase === 'result' ? (
        <ResultWorkspace detail={state.detail} onNewAnalysis={handleClear} />
      ) : (
        <div className="grid gap-6 lg:grid-cols-12">
          {/* Editor column */}
          <section className="space-y-4 lg:col-span-7" aria-label="Text input">
            <div
              className="kc-card p-5"
              onDragOver={(event) => event.preventDefault()}
              onDrop={handleDrop}
            >
              <div className="mb-3 flex items-center justify-between border-b border-line-subtle pb-3">
                <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-dim">
                  Input Stream
                </span>
                {fileName ? (
                  <KeycapBadge tone="graphite">{fileName}</KeycapBadge>
                ) : (
                  <span className="text-[10px] uppercase tracking-[0.14em] text-dim/80">
                    Drop a .txt file here
                  </span>
                )}
              </div>

              <textarea
                ref={textareaRef}
                value={text}
                onChange={(event) => {
                  setText(event.target.value)
                  if (validationError) setValidationError(null)
                }}
                placeholder="Paste text to analyze..."
                rows={10}
                maxLength={MAX_ANALYSIS_TEXT_CHARS + 1000}
                disabled={processing}
                aria-invalid={validationError ? true : undefined}
                aria-describedby={validationError ? 'beam-analysis-error' : 'beam-analysis-counts'}
                className="kc-input resize-y text-sm font-ui leading-relaxed"
              />

              <div
                id="beam-analysis-counts"
                className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-dim"
              >
                <div className="flex items-center gap-4">
                  <span>
                    Chars{' '}
                    <strong className={`font-mono ${overLimit ? 'text-[#FF8A8A]' : 'text-chalk'}`}>
                      {charCount.toLocaleString()}
                    </strong>{' '}
                    / {MAX_ANALYSIS_TEXT_CHARS.toLocaleString()}
                  </span>
                  <span>
                    Words{' '}
                    <strong className="font-mono text-chalk">{wordCount.toLocaleString()}</strong>
                  </span>
                </div>
                {overLimit ? (
                  <span className="font-mono normal-case text-[#FF8A8A]">
                    Over the input limit
                  </span>
                ) : null}
              </div>

              {validationError ? (
                <p
                  id="beam-analysis-error"
                  role="alert"
                  className="mt-3 rounded-keycap border border-[#4A1A1A] bg-[#160D0D] px-3 py-2 text-xs text-[#FF8A8A]"
                >
                  {validationError}
                </p>
              ) : null}
            </div>

            {/* Controls */}
            <div className="kc-card space-y-4 p-5">
              <div className="flex items-center justify-between border-b border-line-subtle pb-3">
                <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-dim">
                  Controls
                </span>
                <KeycapBadge tone="outline">Local run</KeycapBadge>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="flex flex-col gap-2">
                  <span className="text-[11px] font-medium uppercase tracking-[0.14em] text-dim">
                    Source type
                  </span>
                  <select
                    value={sourceType}
                    onChange={(event) => setSourceType(event.target.value as SourceType)}
                    disabled={processing}
                    className="kc-input cursor-pointer py-2"
                  >
                    {SOURCE_TYPES.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-[11px] font-medium uppercase tracking-[0.14em] text-dim">
                    Model
                  </span>
                  <select
                    defaultValue="beam-transformer-v1"
                    disabled
                    className="kc-input cursor-not-allowed py-2 opacity-70"
                    aria-describedby="beam-model-note"
                  >
                    <option value="beam-transformer-v1">beam-transformer-v1 · pending</option>
                  </select>
                  <span id="beam-model-note" className="text-[10px] leading-relaxed text-dim">
                    Transformer weights are not deployed yet — sessions complete without predictions.
                  </span>
                </label>
              </div>

              <div className="flex flex-wrap items-center gap-2.5 border-t border-line-subtle pt-4">
                <button
                  type="button"
                  onClick={handleAnalyze}
                  disabled={processing}
                  className="kc kc--primary px-5 py-2.5 text-xs font-ui font-semibold uppercase tracking-[0.08em]"
                >
                  <Play className="h-3.5 w-3.5" aria-hidden="true" />
                  {processing ? 'Analyzing…' : 'Analyze'}
                </button>
                <button
                  type="button"
                  onClick={handleClear}
                  disabled={processing || (!text && !fileName)}
                  className="kc px-4 py-2.5 text-xs font-ui font-medium uppercase tracking-[0.06em]"
                >
                  <Eraser className="h-3.5 w-3.5" aria-hidden="true" />
                  Clear
                </button>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={processing}
                  className="kc kc--ghost px-4 py-2.5 text-xs font-ui font-medium uppercase tracking-[0.06em]"
                >
                  <UploadCloud className="h-4 w-4" aria-hidden="true" />
                  Upload Text File
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.md,text/plain"
                  onChange={handleFileSelected}
                  className="hidden"
                  aria-label="Upload a plain text file to analyze"
                />
              </div>
            </div>

            <p className="text-[11px] leading-relaxed text-dim">
              B.E.A.M. reports model predictions about emotional expression in submitted text.
              It does not diagnose mental health conditions.
            </p>
          </section>

          {/* Side panel */}
          <aside className="lg:col-span-5" aria-label="Session guidance">
            <div className="kc-card flex h-full min-h-[320px] flex-col items-center justify-center gap-4 p-8 text-center">
              <div className="kc pointer-events-none h-12 w-12 rounded-keycap" aria-hidden="true">
                <Play className="h-5 w-5 text-lime" />
              </div>
              <h2 className="font-display text-lg font-semibold uppercase tracking-[0.08em] text-chalk">
                Awaiting input telemetry
              </h2>
              <p className="max-w-xs text-xs leading-relaxed text-dim">
                Paste text into the input stream and press Analyze. Your session is stored
                privately in your account history once submitted.
              </p>
              <ul className="w-full max-w-xs space-y-2 border-t border-line-subtle pt-4 text-left text-[11px] text-dim">
                <li className="flex items-center justify-between gap-3">
                  <span>Max input</span>
                  <span className="font-mono text-mist">{MAX_ANALYSIS_TEXT_CHARS.toLocaleString()} chars</span>
                </li>
                <li className="flex items-center justify-between gap-3">
                  <span>Accepted files</span>
                  <span className="font-mono text-mist">.txt · .md</span>
                </li>
                <li className="flex items-center justify-between gap-3">
                  <span>Prediction output</span>
                  <span className="font-mono text-mist">Pending model</span>
                </li>
              </ul>
            </div>
          </aside>
        </div>
      )}
    </div>
  )
}
