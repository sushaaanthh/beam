import type { ReactNode } from 'react'
import { KeycapCard } from '../keycap'
import { KeycapBadge } from '../keycap'
import { classNames } from '../../utils/classNames'

type FeatureModuleProps = {
  index: string
  title: string
  code: string
  description: string
  icon?: ReactNode
  footer?: ReactNode
  className?: string
}

/**
 * Major pipeline module — a large tactile keycap card used in
 * "Core Capabilities" style sections.
 */
export function FeatureModule({
  index,
  title,
  code,
  description,
  icon,
  footer,
  className,
}: FeatureModuleProps) {
  return (
    <KeycapCard interactive className={classNames('group flex h-full flex-col p-6 sm:p-7', className)}>
      <div className="flex items-start justify-between">
        <div
          aria-hidden="true"
          className="kc pointer-events-none h-11 w-11 rounded-keycap"
        >
          <span className="text-lime">{icon}</span>
        </div>
        <span className="font-display text-3xl font-semibold leading-none text-[#333330] transition-colors duration-150 group-hover:text-lime">
          {index}
        </span>
      </div>

      <h3 className="mt-6 font-display text-xl font-semibold uppercase tracking-wide text-chalk">
        {title}
      </h3>
      <p className="mt-3 text-sm leading-relaxed text-mist">{description}</p>

      <div className="mt-auto flex items-center justify-between gap-3 pt-6">
        <KeycapBadge tone="outline">{code}</KeycapBadge>
        {footer}
      </div>
    </KeycapCard>
  )
}
