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
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { MetricCard } from '../components/MetricCard'
import { useAuth } from '../hooks/useAuth'

const quickActions = [
  {
    title: 'ANALYZE TEXT',
    desc: 'Launch real-time inference console',
    to: '/analysis',
    icon: <Brain className="h-5 w-5 text-[#C7FF4A]" />,
  },
  {
    title: 'UPLOAD FILE',
    desc: 'Batch process raw TXT / PDF files',
    to: '/analysis',
    icon: <Upload className="h-5 w-5 text-[#F5F5F0]" />,
  },
  {
    title: 'IMPORT DATA',
    desc: 'Ingest datasets from corpus sources',
    to: '/datasets',
    icon: <Database className="h-5 w-5 text-[#F5F5F0]" />,
  },
  {
    title: 'VIEW INSIGHTS',
    desc: 'Explore longitudinal behavioral patterns',
    to: '/insights',
    icon: <BarChart3 className="h-5 w-5 text-[#F5F5F0]" />,
  },
]

const recentAnalyses = [
  {
    id: 'AN-8921',
    title: 'Developer retrospective feedback #42',
    source: 'Dev Community Corpus',
    emotion: 'Joy / Fulfillment',
    confidence: '96.4%',
    date: '2026-08-17 16:30',
    status: 'COMPLETED',
  },
  {
    id: 'AN-8920',
    title: 'Quarterly architecture review notes',
    source: 'Technical Forum',
    emotion: 'Contemplation',
    confidence: '89.1%',
    date: '2026-08-17 14:15',
    status: 'COMPLETED',
  },
  {
    id: 'AN-8919',
    title: 'Bug report thread: memory allocation crash',
    source: 'Issue Tracker',
    emotion: 'Frustration / Concern',
    confidence: '92.7%',
    date: '2026-08-17 11:04',
    status: 'COMPLETED',
  },
  {
    id: 'AN-8918',
    title: 'Open source release announcement discussion',
    source: 'Reddit Feed',
    emotion: 'Excitement',
    confidence: '94.0%',
    date: '2026-08-16 21:40',
    status: 'COMPLETED',
  },
]

const emotionDistribution = [
  { label: 'Joy / Contentment', percentage: 38, count: 1842 },
  { label: 'Frustration / Concern', percentage: 24, count: 1163 },
  { label: 'Neutral / Analytical', percentage: 19, count: 921 },
  { label: 'Anticipation', percentage: 12, count: 581 },
  { label: 'Apprehension', percentage: 7, count: 339 },
]

export function DashboardPage() {
  const { user } = useAuth()
  const displayName = user?.username ?? 'Researcher'

  return (
    <div className="space-y-8">
      {/* Dashboard Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-6">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            WORKSPACE // DASHBOARD
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            Welcome back, {displayName}.
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Ready to analyze textual behavior with transformer-backed interpretability?
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/analysis">
            <Button variant="primary" size="md" leftIcon={<Plus className="h-4 w-4 stroke-[2.5]" />}>
              NEW ANALYSIS
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="ANALYSES"
          value="4,846"
          description="+142 recorded today"
          trend={{ value: "8.4%", direction: "up", label: "vs last week" }}
          icon={<Brain className="h-4 w-4 text-[#C7FF4A]" />}
          sparkline={[30, 45, 60, 50, 75, 80, 92]}
        />
        <MetricCard
          title="DATASETS"
          value="12"
          description="3 curated corpus active"
          trend={{ value: "2 new", direction: "neutral" }}
          icon={<Database className="h-4 w-4 text-[#B8B8B0]" />}
          sparkline={[20, 30, 40, 40, 50, 60, 70]}
        />
        <MetricCard
          title="MODELS"
          value="4"
          description="RoBERTa-v1.2 primary"
          trend={{ value: "Active", direction: "up" }}
          icon={<Cpu className="h-4 w-4 text-[#B8B8B0]" />}
          sparkline={[60, 60, 70, 70, 80, 85, 95]}
        />
        <MetricCard
          title="MODEL ACCURACY"
          value="94.8%"
          description="F1 validation score"
          trend={{ value: "+0.6%", direction: "up", label: "checkpoint" }}
          icon={<CheckCircle2 className="h-4 w-4 text-[#C7FF4A]" />}
          sparkline={[85, 87, 89, 91, 93, 94, 94.8]}
        />
      </div>

      {/* Quick Actions Modules */}
      <div>
        <p className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider mb-3">
          KEYCAP QUICK ACTIONS
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <Link key={action.title} to={action.to} className="block">
              <Card
                variant="default"
                padding="none"
                hover
                className="p-5 flex flex-col justify-between h-36 group cursor-pointer border-[#222222] hover:border-[#383838]"
              >
                <div className="flex items-center justify-between">
                  <div className="h-9 w-9 rounded-lg bg-[#141414] border border-[#262626] flex items-center justify-center shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
                    {action.icon}
                  </div>
                  <ArrowUpRight className="h-4 w-4 text-[#555552] group-hover:text-[#C7FF4A] transition-colors" />
                </div>
                <div>
                  <h3 className="font-display text-base font-bold text-[#F5F5F0] group-hover:text-white">
                    {action.title}
                  </h3>
                  <p className="text-[11px] text-[#73736F] mt-0.5">
                    {action.desc}
                  </p>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Grid: Recent Analyses + Emotion Distribution */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Recent Analyses List (7 cols) */}
        <div className="lg:col-span-7">
          <Card variant="default" padding="none" className="p-6">
            <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-4 mb-4">
              <div>
                <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                  INSPECTION FEED
                </span>
                <h3 className="font-display text-xl font-bold text-[#F5F5F0]">
                  RECENT ANALYSES
                </h3>
              </div>
              <Link to="/history">
                <Button variant="ghost" size="sm" rightIcon={<ArrowUpRight className="h-3 w-3" />}>
                  View All
                </Button>
              </Link>
            </div>

            <div className="space-y-2.5">
              {recentAnalyses.map((item) => (
                <div
                  key={item.id}
                  className="rounded-lg bg-[#0C0C0C] border border-[#1E1E1E] p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-[#333333] transition-colors"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] text-[#73736F] bg-[#141414] px-1.5 py-0.5 rounded border border-[#222222]">
                        {item.id}
                      </span>
                      <p className="text-xs font-semibold text-[#F5F5F0] truncate">
                        {item.title}
                      </p>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-[#73736F] mt-1">
                      <span>{item.source}</span>
                      <span>•</span>
                      <span>{item.date}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right">
                      <span className="text-xs font-mono text-[#C7FF4A] block">
                        {item.emotion}
                      </span>
                      <span className="text-[10px] font-mono text-[#73736F]">
                        {item.confidence} conf
                      </span>
                    </div>
                    <Link to="/history">
                      <Button variant="ghost" size="sm" className="px-2 py-1 text-[11px]">
                        Inspect
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Emotion Distribution + System Overview (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Emotion Distribution */}
          <Card variant="default" padding="none" className="p-6">
            <div className="border-b border-[#1C1C1C] pb-3 mb-4">
              <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                AGGREGATE CORPUS
              </span>
              <h3 className="font-display text-xl font-bold text-[#F5F5F0]">
                EMOTION DISTRIBUTION
              </h3>
            </div>

            <div className="space-y-3.5">
              {emotionDistribution.map((item, idx) => (
                <div key={item.label}>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="text-[#B8B8B0]">{item.label}</span>
                    <span className={idx === 0 ? 'text-[#C7FF4A]' : 'text-[#73736F]'}>
                      {item.percentage}% ({item.count})
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-[#161616] overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        idx === 0 ? 'bg-[#C7FF4A]' : 'bg-[#444440]'
                      }`}
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* System Overview */}
          <Card variant="default" padding="none" className="p-6">
            <div className="border-b border-[#1C1C1C] pb-3 mb-4">
              <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                TELEMETRY & HARDWARE
              </span>
              <h3 className="font-display text-xl font-bold text-[#F5F5F0]">
                SYSTEM OVERVIEW
              </h3>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="rounded-lg bg-[#0C0C0C] border border-[#1E1E1E] p-3">
                <span className="text-[10px] text-[#73736F] uppercase font-mono block">Active Model</span>
                <span className="font-mono font-semibold text-[#F5F5F0] mt-1 block">RoBERTa-v1.2</span>
              </div>
              <div className="rounded-lg bg-[#0C0C0C] border border-[#1E1E1E] p-3">
                <span className="text-[10px] text-[#73736F] uppercase font-mono block">Inference Engine</span>
                <span className="font-mono font-semibold text-[#F5F5F0] mt-1 block">TorchScript CUDA</span>
              </div>
              <div className="rounded-lg bg-[#0C0C0C] border border-[#1E1E1E] p-3">
                <span className="text-[10px] text-[#73736F] uppercase font-mono block">Database</span>
                <span className="font-mono font-semibold text-[#F5F5F0] mt-1 block">PostgreSQL 16</span>
              </div>
              <div className="rounded-lg bg-[#0C0C0C] border border-[#1E1E1E] p-3">
                <span className="text-[10px] text-[#73736F] uppercase font-mono block">System Status</span>
                <span className="inline-flex items-center gap-1.5 font-mono font-semibold text-[#C7FF4A] mt-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A] animate-pulse" /> ONLINE
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}