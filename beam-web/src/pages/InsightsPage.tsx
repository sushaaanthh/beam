import {
  BarChart3,
  TrendingUp,
  Activity,
  Sliders,
  Calendar,
  Layers,
  ArrowUpRight,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

export function InsightsPage() {
  const temporalTrends = [
    { period: 'Mon', constructive: 68, friction: 22, neutral: 10 },
    { period: 'Tue', constructive: 74, friction: 18, neutral: 8 },
    { period: 'Wed', constructive: 65, friction: 28, neutral: 7 },
    { period: 'Thu', constructive: 82, friction: 12, neutral: 6 },
    { period: 'Fri', constructive: 88, friction: 8, neutral: 4 },
    { period: 'Sat', constructive: 70, friction: 15, neutral: 15 },
    { period: 'Sun', constructive: 72, friction: 14, neutral: 14 },
  ]

  const featureImportances = [
    { feature: 'Lexical Problem-Solving Density', importance: 0.88, category: 'Linguistic' },
    { feature: 'Attention Attribution to Technical Terms', importance: 0.74, category: 'Transformer' },
    { feature: 'Negation Transition Polarity Shift', importance: 0.62, category: 'Syntactic' },
    { feature: 'Inter-Punctuation Burstiness', importance: 0.45, category: 'Behavioral' },
    { feature: 'Emotive Descriptor Distribution', importance: 0.38, category: 'Semantic' },
  ]

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-4">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            WORKSPACE // LONGITUDINAL ANALYTICS
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            BEHAVIORAL INSIGHTS
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Temporal emotion trends, behavioral signal vectors, and feature importance matrices.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" leftIcon={<Calendar className="h-3.5 w-3.5" />}>
            Past 7 Days
          </Button>
          <Button variant="primary" size="sm">
            Export Insights
          </Button>
        </div>
      </div>

      {/* Grid: Temporal Trends + Feature Importance */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Temporal Trends */}
        <div className="lg:col-span-7">
          <Card variant="default" padding="none" className="p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3">
              <div>
                <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                  TEMPORAL DYNAMICS
                </span>
                <h3 className="font-display text-xl font-bold text-[#F5F5F0]">
                  WEEKLY AFFECTIVE OSCILLATION
                </h3>
              </div>
              <div className="flex items-center gap-4 text-xs font-mono">
                <span className="inline-flex items-center gap-1.5 text-[#C7FF4A]">
                  <span className="h-2 w-2 rounded-full bg-[#C7FF4A]" /> Positive Valence
                </span>
                <span className="inline-flex items-center gap-1.5 text-[#FF6B6B]">
                  <span className="h-2 w-2 rounded-full bg-[#FF6B6B]" /> Friction / Concern
                </span>
              </div>
            </div>

            {/* Bar Chart Representation */}
            <div className="space-y-4 pt-2">
              {temporalTrends.map((t) => (
                <div key={t.period} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono text-[#B8B8B0]">
                    <span>{t.period}</span>
                    <span>
                      <strong className="text-[#C7FF4A]">{t.constructive}%</strong> /{' '}
                      <strong className="text-[#FF6B6B]">{t.friction}%</strong>
                    </span>
                  </div>
                  <div className="h-3 rounded-md bg-[#121212] overflow-hidden flex gap-0.5">
                    <div
                      className="h-full bg-[#C7FF4A] rounded-l"
                      style={{ width: `${t.constructive}%` }}
                    />
                    <div
                      className="h-full bg-[#FF6B6B] rounded-r"
                      style={{ width: `${t.friction}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Feature Importance Matrix */}
        <div className="lg:col-span-5">
          <Card variant="default" padding="none" className="p-6 space-y-5">
            <div className="border-b border-[#1C1C1C] pb-3">
              <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                GLOBAL ATTRIBUTION
              </span>
              <h3 className="font-display text-xl font-bold text-[#F5F5F0]">
                FEATURE IMPORTANCE (SHAP)
              </h3>
            </div>

            <div className="space-y-4 pt-1">
              {featureImportances.map((feat) => (
                <div key={feat.feature} className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium text-[#F5F5F0] truncate mr-2">
                      {feat.feature}
                    </span>
                    <span className="font-mono text-[#C7FF4A]">
                      {feat.importance.toFixed(2)}
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full bg-[#161616] overflow-hidden">
                    <div
                      className="h-full bg-[#C7FF4A] rounded-full"
                      style={{ width: `${feat.importance * 100}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-mono text-[#73736F] uppercase block">
                    Category: {feat.category}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
