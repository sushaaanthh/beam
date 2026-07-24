import { Card } from '../components/Card'
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
        title="Analysis workspace placeholder"
        description="The page is ready for the future input form and result summary, but no model execution is implemented here."
      />

      <div className="grid gap-5 lg:grid-cols-3">
        {analysisCards.map((card) => (
          <Card key={card} className="min-h-40 text-sm leading-7 text-slate-600 dark:text-slate-300">
            {card}
          </Card>
        ))}
      </div>
    </div>
  )
}