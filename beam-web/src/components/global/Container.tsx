import type { ElementType, HTMLAttributes } from 'react'
import { classNames } from '../../utils/classNames'

type ContainerProps = HTMLAttributes<HTMLElement> & {
  as?: ElementType
}

export function Container({
  as: Tag = 'div',
  className,
  children,
  ...props
}: ContainerProps) {
  return (
    <Tag
      className={classNames(
        'mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8',
        className,
      )}
      {...props}
    >
      {children}
    </Tag>
  )
}
