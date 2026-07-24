import { Card } from '../components/Card'
import { SectionHeading } from '../components/SectionHeading'

const historyEntries = [
  {
    title: 'Session 024',
    description: 'Recent analysis results will appear here once session persistence is implemented.',
    meta: 'Today • No charting yet',
  },
  {
    title: 'Session 023',
    description: 'Historical review cards are prepared for future model output and audit notes.',
    meta: 'Yesterday • Shell only',
  },
  {
    title: 'Session 022',
    description: 'Reserved for explainability traces, labels, and user comments.',
    meta: 'Earlier this week • Placeholder',
  },
]

export function HistoryPage() {
  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="History"
        title="Session history"
        description="A clean scaffold for previous analysis records, designed like a real product table without introducing charts or AI output yet."
      />

      <div className="space-y-4">
        {historyEntries.map((entry) => (
          <Card key={entry.title} className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">{entry.title}</h3>
              <p className="mt-1 text-sm leading-7 text-white/62">{entry.description}</p>
            </div>
            <p className="text-sm font-medium text-white/46">{entry.meta}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}