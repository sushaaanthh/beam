import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Brain,
  Upload,
  Database,
  BarChart3,
  ArrowUpRight,
  Plus,
  Cpu,
  Layers,
  CheckCircle2,
  HeartPulse,
  Flame,
  FileText,
  Mic,
  MessageSquare,
  Sparkles,
  RefreshCw,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { MetricCard } from '../components/MetricCard'
import { WeeklyCheckInModal } from '../components/WeeklyCheckInModal'
import { CompanionDrawer } from '../components/CompanionDrawer'
import { useAuth } from '../hooks/useAuth'
import { beamApi, DashboardSummary, WellnessMetrics } from '../services/api/beam'

export function DashboardPage() {
  const { user } = useAuth()
  const displayName = user?.username ?? 'Researcher'

  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [checkInOpen, setCheckInOpen] = useState(false)
  const [companionOpen, setCompanionOpen] = useState(false)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const res = await beamApi.getDashboardSummary()
      if (res) {
        setSummary(res)
      }
    } catch {
      // Clean zero-initialized fallback for new accounts
      setSummary({
        wellness_gauge: 0,
        dominant_emotion: 'Awaiting First Entry',
        active_streak: 0,
        consistency_score: 0,
        positivity_ratio: 0,
        reflection_meter: 0,
        recovery_score: 0,
        weekly_trend: [
          { day: 'Mon', score: 0, dominant: 'No entries' },
          { day: 'Tue', score: 0, dominant: 'No entries' },
          { day: 'Wed', score: 0, dominant: 'No entries' },
          { day: 'Thu', score: 0, dominant: 'No entries' },
          { day: 'Fri', score: 0, dominant: 'No entries' },
          { day: 'Sat', score: 0, dominant: 'No entries' },
          { day: 'Sun', score: 0, dominant: 'No entries' },
        ],
        word_cloud: [],
        calendar_heatmap: Array.from({ length: 28 }, (_, i) => ({
          day_offset: 28 - i,
          intensity: 0,
          mood: 'No activity',
        })),
        total_journals: 0,
        total_voice_notes: 0,
        recent_journals: [],
        recent_voice_notes: [],
        ai_insights: [
          'Welcome to BEAM AI! Create your first reflection in the Affective Studio to unlock longitudinal telemetry.',
          'Complete a Sunday check-in or voice note to calibrate your personalized Wellness Score.',
          'Longitudinal behavioral patterns will automatically populate as you record entries.',
        ],
        unread_notifications: 1,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCheckInSuccess = (metrics: WellnessMetrics) => {
    if (summary) {
      setSummary({
        ...summary,
        wellness_gauge: metrics.wellness_score,
        consistency_score: metrics.consistency_score,
        positivity_ratio: metrics.positive_ratio,
        reflection_meter: metrics.reflection_score,
        dominant_emotion: metrics.dominant_emotion,
        weekly_trend: metrics.weekly_trend,
      })
    }
  }

  const isNewAccount = (summary?.total_journals ?? 0) === 0

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Dashboard Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-6">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            BEAM AI // LONGITUDINAL DASHBOARD
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            Welcome back, {displayName}.
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Longitudinal affective timeline, explainable insights, and behavioral wellness modeling.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="md"
            onClick={() => setCheckInOpen(true)}
            leftIcon={<HeartPulse className="h-4 w-4 text-[#C7FF4A]" />}
          >
            Weekly Check-in
          </Button>

          <Button
            variant="secondary"
            size="md"
            onClick={() => setCompanionOpen(true)}
            leftIcon={<MessageSquare className="h-4 w-4 text-[#C7FF4A]" />}
          >
            AI Companion
          </Button>

          <Link to="/analysis">
            <Button variant="primary" size="md" leftIcon={<Plus className="h-4 w-4 stroke-[2.5]" />}>
              NEW ENTRY
            </Button>
          </Link>
        </div>
      </div>

      {/* Wellness & Behavioral Metrics Row */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="WELLNESS GAUGE"
          value={isNewAccount ? "0 / 100" : `${summary?.wellness_gauge ?? 0} / 100`}
          description={isNewAccount ? "Awaiting first reflection" : "Formula: (Cons×0.3)+(Pos×0.4)+(Eng×0.3)"}
          trend={{ value: isNewAccount ? "Init" : "+4.2%", direction: isNewAccount ? "neutral" : "up" }}
          icon={<HeartPulse className="h-4 w-4 text-[#C7FF4A]" />}
          sparkline={isNewAccount ? [0, 0, 0, 0, 0, 0, 0] : [70, 75, 78, 80, 82, 85, summary?.wellness_gauge ?? 84]}
        />
        <MetricCard
          title="ACTIVE STREAK"
          value={`${summary?.active_streak ?? 0} Days`}
          description={isNewAccount ? "Start your daily streak" : "Consistent daily journaling"}
          trend={{ value: isNewAccount ? "0 Days" : "Active", direction: isNewAccount ? "neutral" : "up" }}
          icon={<Flame className="h-4 w-4 text-[#FF6B6B]" />}
          sparkline={isNewAccount ? [0, 0, 0, 0, 0, 0, 0] : [1, 2, 3, 4, 4, 4, 4]}
        />
        <MetricCard
          title="REFLECTION DEPTH"
          value={isNewAccount ? "0 / 100" : `${summary?.reflection_meter ?? 0} / 100`}
          description={isNewAccount ? "Lexical depth metric" : "Lexical complexity & depth"}
          trend={{ value: isNewAccount ? "Init" : "+12.0%", direction: isNewAccount ? "neutral" : "up" }}
          icon={<Brain className="h-4 w-4 text-[#C7FF4A]" />}
          sparkline={isNewAccount ? [0, 0, 0, 0, 0, 0, 0] : [60, 70, 75, 80, 85, 88, summary?.reflection_meter ?? 89]}
        />
        <MetricCard
          title="DOMINANT EMOTION"
          value={summary?.dominant_emotion ?? "Awaiting Data"}
          description={isNewAccount ? "Record first entry" : "Stable longitudinal state"}
          trend={{ value: isNewAccount ? "No data" : "Positive", direction: isNewAccount ? "neutral" : "up" }}
          icon={<CheckCircle2 className="h-4 w-4 text-[#C7FF4A]" />}
          sparkline={isNewAccount ? [0, 0, 0, 0, 0, 0, 0] : [80, 82, 85, 88, 90, 92, 94]}
        />
      </div>

      {/* Grid: Weekly Affective Oscillation + 28-Day Mood Heatmap */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Weekly Trend (7 cols) */}
        <div className="lg:col-span-7">
          <Card variant="default" padding="none" className="p-6 space-y-5 border-[#222222]">
            <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3">
              <div>
                <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                  LONGITUDINAL TELEMETRY
                </span>
                <h3 className="font-display text-xl font-bold text-[#F5F5F0]">
                  WEEKLY AFFECTIVE OSCILLATION
                </h3>
              </div>
              <span className="text-xs font-mono text-[#C7FF4A]">
                {isNewAccount ? "0 entries recorded" : `Average: ${summary?.wellness_gauge ?? 0}%`}
              </span>
            </div>

            {/* Bar & Trend Visualizer */}
            <div className="space-y-3.5 pt-1">
              {summary?.weekly_trend.map((day) => (
                <div key={day.day} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-[#F5F5F0] font-semibold">{day.day}</span>
                    <span className="text-[#73736F]">
                      <strong className={day.score > 0 ? "text-[#C7FF4A]" : "text-[#555552]"}>{day.score}%</strong> • {day.dominant}
                    </span>
                  </div>
                  <div className="h-2.5 rounded-md bg-[#121212] overflow-hidden">
                    <div
                      className="h-full bg-[#C7FF4A] rounded-md transition-all duration-500"
                      style={{ width: `${day.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* 28-Day Calendar Activity Heatmap + Word Cloud (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Calendar Heatmap */}
          <Card variant="default" padding="none" className="p-6 border-[#222222]">
            <div className="border-b border-[#1C1C1C] pb-3 mb-4">
              <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                ACTIVITY & REFLECTION FREQUENCY
              </span>
              <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
                28-DAY MOOD HEATMAP
              </h3>
            </div>

            {/* Heatmap Grid */}
            <div className="grid grid-cols-7 gap-2">
              {summary?.calendar_heatmap.map((item, idx) => (
                <div
                  key={idx}
                  title={`Day ${item.day_offset}: ${item.mood}`}
                  className={`h-7 rounded-md border transition-all flex items-center justify-center text-[10px] font-mono ${
                    item.intensity === 4
                      ? 'bg-[#C7FF4A] text-[#080808] border-[#C7FF4A]'
                      : item.intensity === 3
                      ? 'bg-[#C7FF4A]/60 text-white border-[#C7FF4A]/40'
                      : item.intensity === 2
                      ? 'bg-[#C7FF4A]/30 text-[#B8B8B0] border-[#C7FF4A]/20'
                      : 'bg-[#121212] text-[#444440] border-[#1C1C1C]'
                  }`}
                >
                  {item.day_offset}
                </div>
              ))}
            </div>
            <div className="flex items-center justify-between text-[10px] font-mono text-[#73736F] mt-3 pt-2 border-t border-[#1C1C1C]">
              <span>No Activity</span>
              <div className="flex items-center gap-1">
                <span className="h-2 w-2 rounded bg-[#121212] border border-[#1C1C1C]" />
                <span className="h-2 w-2 rounded bg-[#C7FF4A]/30" />
                <span className="h-2 w-2 rounded bg-[#C7FF4A]/60" />
                <span className="h-2 w-2 rounded bg-[#C7FF4A]" />
              </div>
              <span>Peak Positive</span>
            </div>
          </Card>

          {/* Word Cloud Chips */}
          <Card variant="default" padding="none" className="p-6 border-[#222222]">
            <div className="border-b border-[#1C1C1C] pb-3 mb-3">
              <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                KEYWORD ATTRIBUTION
              </span>
              <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
                AFFECTIVE WORD CLOUD
              </h3>
            </div>

            {summary?.word_cloud && summary.word_cloud.length > 0 ? (
              <div className="flex flex-wrap gap-2 pt-1">
                {summary.word_cloud.map((w) => (
                  <span
                    key={w.text}
                    className="px-2.5 py-1 rounded-lg text-xs font-mono bg-[#141414] border border-[#242424] text-[#C7FF4A] hover:scale-105 transition-transform cursor-default"
                    style={{ opacity: Math.min(1.0, 0.4 + w.value / 80) }}
                  >
                    #{w.text}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#73736F] py-3 leading-relaxed">
                No affective keywords extracted yet. Record a reflection or voice note in the Affective Studio to generate your personalized word cloud.
              </p>
            )}
          </Card>
        </div>
      </div>

      {/* Personalized AI Insights */}
      <Card variant="elevated" padding="none" className="p-6 border-[#2A2A2A]">
        <div className="flex items-center gap-2 border-b border-[#1C1C1C] pb-3 mb-4">
          <Sparkles className="h-4 w-4 text-[#C7FF4A]" />
          <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
            BEAM AI Longitudinal Observations
          </h3>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {summary?.ai_insights.map((ins, i) => (
            <div key={i} className="rounded-xl bg-[#0E0E0E] border border-[#1E1E1E] p-4 text-xs text-[#B8B8B0] leading-relaxed">
              <span className="font-mono text-[#C7FF4A] font-bold block mb-1">0{i + 1} // INSIGHT</span>
              {ins}
            </div>
          ))}
        </div>
      </Card>

      {/* Modals & Drawers */}
      <WeeklyCheckInModal
        isOpen={checkInOpen}
        onClose={() => setCheckInOpen(false)}
        onSuccess={handleCheckInSuccess}
      />
      <CompanionDrawer
        isOpen={companionOpen}
        onClose={() => setCompanionOpen(false)}
      />
    </div>
  )
}