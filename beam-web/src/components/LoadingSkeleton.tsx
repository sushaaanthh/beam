import { classNames } from '../utils/classNames'

type LoadingSkeletonProps = {
  className?: string
}

export function LoadingSkeleton({ className }: LoadingSkeletonProps) {
  return (
    <div className={classNames('rounded-[14px] bg-[#101010] border border-[#222222] animate-pulse p-6 space-y-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]', className)}>
      <div className="h-3 w-24 rounded bg-[#1C1C1C]" />
      <div className="h-7 w-2/3 rounded bg-[#222222]" />
      <div className="space-y-2.5 pt-2">
        <div className="h-3 w-full rounded bg-[#181818]" />
        <div className="h-3 w-5/6 rounded bg-[#181818]" />
        <div className="h-3 w-3/5 rounded bg-[#181818]" />
      </div>
    </div>
  )
}
