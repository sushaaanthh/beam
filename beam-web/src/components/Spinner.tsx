export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-3',
  }

  return (
    <div className="flex items-center justify-center p-2">
      <div className={`${sizeClasses[size]} animate-spin rounded-full border-[#262626] border-t-[#C7FF4A]`} />
    </div>
  )
}