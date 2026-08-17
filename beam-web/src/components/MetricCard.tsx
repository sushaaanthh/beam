import { Card } from './Card'

type MetricCardProps = {
  title: string
  value: string | number
  description?: string
  trend?: {
    value: string
    direction: 'up' | 'down' | 'neutral'
    label?: string
  }
  icon?: ReactNode?: string
  className?: string
}

export function MetricCard({
  title,
  value,
  description,
  trend,
  icon,
  className,
}: MetricCardProps) {
  return (
    <Card
      variant="glass"
      padding="md"
      hover
      className={`relative overflow-hidden ${className}`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-apple-accent/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

      <div className="relative flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-caption-sm font-semibold uppercase tracking-wider text-apple-textTertiary">
            {title}
          </p>
          {description && (
            <p className="mt-1.5 text-body-sm text-apple-textSecondary line-clamp-2">{description}</p>
          )}
        </div>

        {icon && (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-apple-lg bg-apple-accentSoft text-apple-accent" aria-hidden="true">
            {icon}
          </div>
        )}

        {trend && (
          <div
            className={`flex shrink-0 items-center gap-1.5 text-caption-sm font-semibold ${
              trend.direction === 'up'
                ? 'text-apple-success'
                : trend.direction === 'down'
                ? 'text-apple-danger'
                : 'text-apple-textTertiary'
            }`}
          >
            {trend.direction === 'up' && (
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                <path d="M18 15l-6-6-6 6" />
              </svg>
            )}
            {trend.direction === 'down' && (
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                <path d="M6 9l6 6 6-6" />
              </svg>
            )}
            {trend.direction === 'neutral' && (
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                <path d="M5 12h14" />
              </svg>
            )}
            <span>{trend.value}</span>
            {trend.label && <span className="text-apple-textTertiary">{trend.label}</span>}
          </div>
        )}
      </div>

      <div className="relative mt-4">
        <p className="text-display-sm font-semibold tracking-tight text-apple-textPrimary">
          {value}
        </p>
      </div>
    </Card>
  )
}