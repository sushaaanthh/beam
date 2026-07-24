import { Card } from '../components/Card'
import { SectionHeading } from '../components/SectionHeading'
import { StatCard } from '../components/StatCard'
import { Button } from '../components/Button'

const dashboardCards = [
  {
    title: 'Recent Analysis',
    value: 'No results yet',
    description: 'Latest analysis summaries will appear here once the analysis workflow is connected.',
  },
  {
    title: 'Behavior Summary',
    value: 'Awaiting data',
    description: 'Behavioral patterns and account-level summaries will be surfaced from future sessions.',
  },
  {
    title: 'Emotion Prediction',
    value: 'Placeholder',
    description: 'This card will eventually reflect model output, confidence, and explanation metadata.',
  },
  {
    title: 'Latest Sessions',
    value: '0 active',
    description: 'Session history will be populated when the data workflow is enabled.',
  },
]

const quickActions = [
  'Start a new analysis session',
  'Review the latest behavior trends',
  'Check your saved session history',
]

export function DashboardPage() {
  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Dashboard"
        title="Professional dashboard shell"
        description="This area is intentionally placeholder-driven for now, but the layout is ready for real analysis components later."
      />

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {dashboardCards.map((card) => (
          <StatCard key={card.title} {...card} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="space-y-5">
          <SectionHeading title="Quick Actions" description="Common actions a researcher will take from the first release." />
          <div className="grid gap-4 sm:grid-cols-2">
            {quickActions.map((action) => (
              <button
                key={action}
                type="button"
                className="rounded-[1.25rem] border border-slate-200 bg-slate-50 px-4 py-4 text-left text-sm font-medium text-slate-700 transition hover:border-sky-300 hover:bg-sky-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200 dark:hover:border-sky-500/40 dark:hover:bg-slate-900"
              >
                {action}
              </button>
            ))}
          </div>
          <Button variant="secondary" className="w-full sm:w-auto">
            Explore analysis workspace
          </Button>
        </Card>

        <Card className="space-y-5">
          <SectionHeading title="Session health" description="A compact summary of what the shell is ready to support." />
          <div className="space-y-4 text-sm text-slate-600 dark:text-slate-300">
            {[
              'Protected route access is active.',
              'JWT session refresh is configured at the client layer.',
              'React Query is ready for session and profile data.',
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-slate-200 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950">
                {item}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}