import { Card } from './Card'

type StatCardProps = {
  title: string
  value: string
  description: string
  accent?: string
}

export function StatCard({ title, value, description, accent = 'from-sky-500 to-cyan-400' }: StatCardProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${accent}`} />
      <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">{value}</p>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{description}</p>
    </Card>
  )
}