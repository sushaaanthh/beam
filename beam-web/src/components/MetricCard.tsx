import { Card } from './Card'

type MetricCardProps = {
  title: string
  value: string
  description: string
}

export function MetricCard({ title, value, description }: MetricCardProps) {
  return (
    <Card className="relative overflow-hidden space-y-3 p-5">
      <div className="absolute inset-x-0 top-0 h-px bg-white/10" />
      <div className="flex items-center justify-between gap-3">
        <p className="text-[0.7rem] uppercase tracking-[0.32em] text-white/42">{title}</p>
        <span className="h-2 w-2 rounded-full bg-[#a6b1ff]/70" aria-hidden="true" />
      </div>
      <p className="text-3xl font-semibold tracking-tight text-white">{value}</p>
      <p className="text-sm leading-6 text-white/62">{description}</p>
    </Card>
  )
}