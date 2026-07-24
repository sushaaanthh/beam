import { classNames } from '../utils/classNames'

type LoadingSkeletonProps = {
  className?: string
}

export function LoadingSkeleton({ className }: LoadingSkeletonProps) {
  return (
    <div className={classNames('animate-pulse rounded-[1.125rem] border border-white/10 bg-white/4 p-6', className)}>
      <div className="space-y-4">
        <div className="h-3 w-24 rounded-full bg-white/10" />
        <div className="h-7 w-2/3 rounded-full bg-white/12" />
        <div className="space-y-3 pt-2">
          <div className="h-3 w-full rounded-full bg-white/8" />
          <div className="h-3 w-5/6 rounded-full bg-white/8" />
          <div className="h-3 w-3/5 rounded-full bg-white/8" />
        </div>
      </div>
    </div>
  )
}