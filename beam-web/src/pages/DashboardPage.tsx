import { Card } from '../components/Card'
import { EmptyState } from '../components/EmptyState'
import { MetricCard } from '../components/MetricCard'
import { SectionHeading } from '../components/SectionHeading'
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
        title="Workspace overview"
        description="A productivity-first shell for analysis, history, and session management. The layout stays quiet until the data layer is ready."
      />

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {dashboardCards.map((card) => (
          <MetricCard key={card.title} {...card} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="space-y-5">
          <SectionHeading title="Quick actions" description="Common actions surfaced as keycap controls." />
          <div className="grid gap-4 sm:grid-cols-2">
            {quickActions.map((action) => (
              <button
                key={action}
                type="button"
                className="rounded-[1rem] border border-white/10 bg-white/4 px-4 py-4 text-left text-sm font-medium text-white/78 transition duration-200 hover:-translate-y-px hover:border-white/16 hover:bg-white/6 active:translate-y-px"
              >
                {action}
              </button>
            ))}
          </div>
          <Button variant="secondary" className="w-full sm:w-auto">
            Explore analysis workspace
          </Button>
        </Card>

        <EmptyState
          eyebrow="Session health"
          title="No live analysis streams yet"
          description="This shell is ready for future model output, audit notes, and session metrics. For now, the workspace stays intentionally quiet."
          action={(
            <div className="grid gap-3 sm:grid-cols-3">
              {['Protected access', 'JWT refresh', 'Query ready'].map((item) => (
                <div key={item} className="rounded-[1rem] border border-white/10 bg-white/4 px-4 py-3 text-sm text-white/68">
                  {item}
                </div>
              ))}
            </div>
          )}
        />
      </div>
    </div>
  )
}