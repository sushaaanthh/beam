import type { ReactNode } from 'react'
import { classNames } from '../../utils/classNames'

type TechnicalLabelProps = {
  children: ReactNode
  tone?: 'graphite' | 'lime'
  as?: 'span' | 'div' | 'p'
  className?: string
}

export function TechnicalLabel({ children, tone = 'graphite', as: Tag = 'span', className }: TechnicalLabelProps) {
  return (
    <Tag
      className={classNames(
        'tech-label font-ui',
        tone === 'lime' && 'tech-label--lime',
        className,
      )}
    >
      {children}
    </Tag>
  )
}
