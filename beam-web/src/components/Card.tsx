import type { HTMLAttributes } from 'react'

import { classNames } from '../utils/classNames'

type CardProps = HTMLAttributes<HTMLDivElement>

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={classNames(
        'rounded-[1.125rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.025))] p-6 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.06),0_18px_50px_rgba(0,0,0,0.4)] transition duration-200 hover:-translate-y-px hover:border-white/14',
        className,
      )}
      {...props}
    />
  )
}

export function KeycapCard(props: CardProps) {
  return <Card {...props} />
}