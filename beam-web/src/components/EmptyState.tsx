import type { ReactNode } from 'react'

import { Card } from './Card'

type EmptyStateProps = {
  title: string
  description: string
  eyebrow?: string
  action?: ReactNode
  className?: string
}

export function EmptyState({ title, description, eyebrow, action, className }: EmptyStateProps) {
  return (
    <Card className={className ?? 'text-center'}>
      <div className="space-y-4">
        {eyebrow ? <p className="text-[0.7rem] uppercase tracking-[0.34em] text-white/42">{eyebrow}</p> : null}
        <h3 className="text-2xl font-semibold tracking-tight text-white">{title}</h3>
        <p className="mx-auto max-w-2xl text-sm leading-7 text-white/62">{description}</p>
        {action ? <div className="pt-2">{action}</div> : null}
      </div>
    </Card>
  )
}