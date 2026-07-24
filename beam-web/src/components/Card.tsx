import type { HTMLAttributes } from 'react'

import { classNames } from '../utils/classNames'

type CardProps = HTMLAttributes<HTMLDivElement>

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={classNames(
        'kds-keycap kds-keycap-interactive rounded-[18px] p-6 text-white',
        className,
      )}
      {...props}
    />
  )
}

export function KeycapCard(props: CardProps) {
  return <Card {...props} />
}
