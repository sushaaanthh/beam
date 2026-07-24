import { Card } from '../components/Card'
import { EmptyState } from '../components/EmptyState'
import { SectionHeading } from '../components/SectionHeading'

const analysisCards = [
  'Input session details and text samples here later.',
  'Review explainability outputs once the AI layer is integrated.',
  'Reserve space for labels, confidence values, and notes.',
]

export function AnalysisPage() {
  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Analysis"
        title="Analysis workspace"
        description="The page is staged for future input forms and result summaries, but no model execution is implemented here."
      />

      <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <EmptyState
          eyebrow="Shell ready"
          title="No analysis input connected yet"
          description="The future analysis form will live here, alongside explainability notes, labels, and model metadata."
          action={(
            <div className="flex flex-wrap items-center justify-center gap-3">
              <span className="rounded-full border border-white/10 bg-white/4 px-4 py-2 text-sm text-white/68">Input lane</span>
              <span className="rounded-full border border-white/10 bg-white/4 px-4 py-2 text-sm text-white/68">Explainability lane</span>
              <span className="rounded-full border border-white/10 bg-white/4 px-4 py-2 text-sm text-white/68">Output lane</span>
            </div>
          )}
        />

        <div className="grid gap-5">
          {analysisCards.map((card) => (
            <Card key={card} className="min-h-32 text-sm leading-7 text-white/66">
              {card}
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}