import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'

import type {
  AnalysisDetail,
  BehaviorMetricsPayload,
  EmotionDistributionItem,
  ExplanationPayload,
  PredictionPayload,
} from '../../types/analysis'
import { KeycapBadge, KeycapPanel } from '../keycap'
import { TechnicalLabel } from '../global'

function SectionHeader({ title, available }: { title: string; available: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-dim">{title}</span>
      <KeycapBadge tone={available ? 'lime' : 'outline'}>
        {available ? 'Available' : 'Pending model'}
      </KeycapBadge>
    </div>
  )
}

function UnavailableNote() {
  return (
    <p className="text-xs leading-relaxed text-dim">
      The B.E.A.M. transformer is not deployed yet. This section will populate with real
      inference output once the model is connected — nothing is estimated in its place.
    </p>
  )
}

function formatConfidence(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

const behaviorMetricLabels: Array<{ key: keyof BehaviorMetricsPayload; label: string }> = [
  { key: 'positivity_score', label: 'Positivity' },
  { key: 'negativity_score', label: 'Negativity' },
  { key: 'engagement_score', label: 'Engagement' },
  { key: 'linguistic_complexity', label: 'Linguistic Complexity' },
  { key: 'emotional_variance', label: 'Emotional Variance' },
  { key: 'posting_frequency', label: 'Posting Frequency' },
]

export function ResultWorkspace({
  detail,
  onNewAnalysis,
}: {
  detail: AnalysisDetail
  onNewAnalysis: () => void
}) {
  const prediction: PredictionPayload | null = detail.prediction
  const hasPrediction = prediction?.primary_emotion != null && prediction?.confidence != null
  const distribution: EmotionDistributionItem[] | null =
    hasPrediction ? prediction?.emotion_distribution ?? null : null
  const metrics = detail.behavior_metrics
  const explanation: ExplanationPayload | null = detail.explanation

  return (
    <div className="space-y-5" aria-live="polite">
      {/* Primary emotion + confidence */}
      <KeycapPanel
        eyebrow="Inference Report"
        title={detail.title ?? 'Untitled Session'}
        meta={<TechnicalLabel tone={detail.status === 'completed' ? 'lime' : 'graphite'}>{detail.status}</TechnicalLabel>}
      >
        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-3">
            <SectionHeader title="Primary Emotion" available={hasPrediction} />
            {hasPrediction ? (
              <p className="font-display text-3xl font-semibold uppercase tracking-wide text-chalk">
                {prediction?.primary_emotion}
              </p>
            ) : (
              <UnavailableNote />
            )}
          </div>

          <div className="space-y-3">
            <SectionHeader title="Confidence" available={hasPrediction} />
            {hasPrediction ? (
              <>
                <div className="flex items-baseline gap-3">
                  <span className="font-display text-4xl font-semibold leading-none text-lime">
                    {formatConfidence(prediction?.confidence ?? 0)}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-raised shadow-well">
                  <div
                    className="h-full rounded-full bg-lime"
                    style={{ width: `${Math.min(100, (prediction?.confidence ?? 0) * 100)}%` }}
                  />
                </div>
              </>
            ) : (
              <UnavailableNote />
            )}
          </div>
        </div>
      </KeycapPanel>

      {/* Emotion distribution */}
      <KeycapPanel
        eyebrow="Model Prediction"
        title="Emotion Distribution"
        meta={
          distribution ? (
            <TechnicalLabel>{distribution.length} classes</TechnicalLabel>
          ) : undefined
        }
      >
        {distribution && distribution.length > 0 ? (
          <ul className="space-y-3">
            {distribution.map((entry) => (
              <li key={entry.label} className="space-y-1.5">
                <div className="flex justify-between text-[11px] font-medium tracking-wide">
                  <span className="uppercase text-mist">{entry.label}</span>
                  <span className="font-mono text-dim">{(entry.score * 100).toFixed(1)}%</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-raised">
                  <div
                    className="h-full rounded-full bg-lime/80"
                    style={{ width: `${Math.min(100, entry.score * 100)}%` }}
                  />
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <UnavailableNote />
        )}
      </KeycapPanel>

      {/* Behavioral signals */}
      <KeycapPanel
        eyebrow="Observed Pattern"
        title="Behavioral Signals"
        meta={metrics ? <TechnicalLabel>6 metrics</TechnicalLabel> : undefined}
      >
        {metrics ? (
          <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {behaviorMetricLabels.map(({ key, label }) => {
              const value = metrics[key]
              return (
                <div
                  key={key}
                  className="rounded-keycap border border-line-subtle bg-surface p-3 shadow-well"
                >
                  <dt className="text-[9px] font-medium uppercase tracking-[0.16em] text-dim">
                    {label}
                  </dt>
                  <dd className="mt-1 font-mono text-sm text-chalk">
                    {value != null ? value.toFixed(3) : '—'}
                  </dd>
                </div>
              )
            })}
          </dl>
        ) : (
          <UnavailableNote />
        )}
      </KeycapPanel>

      {/* Explainability */}
      <KeycapPanel
        eyebrow="Evidence Trail"
        title="Explainability"
        meta={
          explanation?.method ? <TechnicalLabel>{explanation.method}</TechnicalLabel> : undefined
        }
      >
        {explanation ? (
          <div className="space-y-4">
            {explanation.summary ? (
              <p className="text-sm leading-relaxed text-mist">{explanation.summary}</p>
            ) : null}
            {explanation.important_keywords && explanation.important_keywords.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {explanation.important_keywords.map((keyword) => (
                  <TechnicalLabel key={keyword}>{keyword}</TechnicalLabel>
                ))}
              </div>
            ) : null}
          </div>
        ) : (
          <UnavailableNote />
        )}
      </KeycapPanel>

      {/* Model information */}
      <KeycapPanel eyebrow="System" title="Model Information">
        <dl className="grid gap-x-8 gap-y-3 text-xs sm:grid-cols-2">
          <div className="flex justify-between gap-4 sm:block">
            <dt className="text-dim">Service</dt>
            <dd className="font-mono text-mist sm:mt-1">
              {detail.model_info.model_name ?? '—'}
            </dd>
          </div>
          <div className="flex justify-between gap-4 sm:block">
            <dt className="text-dim">Version</dt>
            <dd className="font-mono text-mist sm:mt-1">
              {detail.model_info.model_version ?? 'unversioned'}
            </dd>
          </div>
          <div className="flex justify-between gap-4 sm:block">
            <dt className="text-dim">Inference time</dt>
            <dd className="font-mono text-mist sm:mt-1">
              {prediction?.inference_time_ms != null
                ? `${prediction.inference_time_ms} ms`
                : '—'}
            </dd>
          </div>
          <div className="flex justify-between gap-4 sm:block">
            <dt className="text-dim">Status</dt>
            <dd className="sm:mt-1">
              <KeycapBadge tone={detail.model_info.deployed ? 'lime' : 'outline'}>
                {detail.model_info.deployed ? 'Deployed' : 'Not deployed'}
              </KeycapBadge>
            </dd>
          </div>
          {detail.model_info.note ? (
            <div className="col-span-full">
              <dt className="sr-only">Note</dt>
              <dd className="rounded-keycap border border-line-subtle bg-surface p-3 text-[11px] leading-relaxed text-dim">
                {detail.model_info.note}
              </dd>
            </div>
          ) : null}
        </dl>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-line-subtle pt-4">
          <p className="max-w-md text-[11px] leading-relaxed text-dim">
            B.E.A.M. reports model predictions about emotional expression in text.
            It does not diagnose mental health conditions.
          </p>
          <Actions onNewAnalysis={onNewAnalysis} sessionId={detail.session_id} />
        </div>
      </KeycapPanel>
    </div>
  )
}

function Actions({ onNewAnalysis, sessionId }: { onNewAnalysis: () => void; sessionId: string }): ReactNode {
  return (
    <div className="flex flex-wrap items-center gap-2.5">
      <Link to="/history" className="kc px-3 py-1.5 text-xs font-ui font-medium uppercase tracking-[0.06em] kc--ghost">
        View History
      </Link>
      <button
        type="button"
        onClick={() => navigator.clipboard?.writeText(sessionId).catch(() => undefined)}
        className="kc px-3 py-1.5 text-xs font-ui font-medium uppercase tracking-[0.06em]"
      >
        Copy Session ID
      </button>
      <button
        type="button"
        onClick={onNewAnalysis}
        className="kc kc--primary px-4 py-2 text-xs font-ui font-semibold uppercase tracking-[0.06em]"
      >
        New Analysis →
      </button>
    </div>
  )
}
