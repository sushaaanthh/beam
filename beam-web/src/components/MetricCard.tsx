import type { ReactNode } from 'react'
import { Card } from './Card'

export type MetricCardProps = {
  title: string
  value: string | number
  description?: string
  trend?: {
    value: string
    direction: 'up' | 'down' | 'neutral'
    label?: string
  }
  icon?: ReactNode
  className?: string
  sparkline?: number[]
}

export function MetricCard({
  title,
  value,
  description,
  trend,
  icon,
  className = '',
  sparkline = [40, 55, 45, 60, 75, 70, 85],
}: MetricCardProps) {
  return (
    <Card
      variant="default"
      padding="none"
      hover
      className={`p-5 relative overflow-hidden group ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="text-[10px] font-medium tracking-[0.14em] uppercase text-[#73736F]">
            {title}
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="font-display text-3xl font-bold tracking-tight text-[#F5F5F0]">
              {value}
            </span>
          </div>
        </div>

        {icon ? (
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#141414] border border-[#262626] text-[#B8B8B0] shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]" aria-hidden="true">
            {icon}
          </div>
        ) : null}
      </div>

      <div className="mt-4 flex items-center justify-between pt-3 border-t border-[#1C1C1C]">
        {description && (
          <span className="text-xs text-[#B8B8B0] truncate">
            {description}
          </span>
        )}

        {trend && (
          <div
            className={`flex shrink-0 items-center gap-1 text-xs font-medium ml-auto ${
              trend.direction === 'up'
                ? 'text-[#C7FF4A]'
                : trend.direction === 'down'
                ? 'text-[#FF6B6B]'
                : 'text-[#73736F]'
            }`}
          >
            {trend.direction === 'up' && '▲'}
            {trend.direction === 'down' && '▼'}
            <span>{trend.value}</span>
            {trend.label && <span className="text-[#73736F] text-[10px] ml-1">{trend.label}</span>}
          </div>
        )}
      </div>

      {/* Subtle bottom sparkline visual */}
      <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#161616] overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-transparent via-[#C7FF4A]/40 to-transparent transition-all duration-300 group-hover:via-[#C7FF4A]"
          style={{ width: `${Math.min(100, Math.max(20, (sparkline[sparkline.length - 1] || 50)))}%` }}
        />
      </div>
    </Card>
  )
}