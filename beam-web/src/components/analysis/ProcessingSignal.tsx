import { KeycapPanel } from '../keycap'

/**
 * Restrained processing state — a slow, low-amplitude signal sweep.
 * Global CSS disables animations under prefers-reduced-motion.
 */
export function ProcessingSignal({ sessionId }: { sessionId?: string | undefined }) {
  return (
    <KeycapPanel
      className="mx-auto max-w-md"
      bodyClassName="flex flex-col items-center gap-6 px-8 py-14 text-center"
      aria-live="polite"
      role="status"
    >
      <p className="text-[10px] font-medium uppercase tracking-[0.22em] text-dim">
        Inference Queue
      </p>

      <h2 className="font-display text-2xl font-semibold uppercase tracking-[0.08em] text-chalk">
        Analyzing Text
      </h2>

      {/* Signal sweep */}
      <div className="flex h-10 items-end gap-1.5" aria-hidden="true">
        {[0, 1, 2, 3, 4].map((bar) => (
          <span
            key={bar}
            className={`w-1 rounded-full ${bar === 2 ? 'bg-lime' : 'bg-[#3A3A36]'} beam-pulse`}
            style={{
              height: `${[40, 70, 100, 70, 40][bar]}%`,
              animationDelay: `${bar * 240}ms`,
              animationDuration: '2s',
            }}
          />
        ))}
      </div>

      <div className="w-full space-y-1.5 border-t border-line-subtle pt-4 text-left text-[10px] font-medium uppercase tracking-[0.16em] text-dim">
        <div className="flex justify-between">
          <span>Stage</span>
          <span className="text-mist">Transformer inference</span>
        </div>
        <div className="flex justify-between">
          <span>Session</span>
          <span className="font-mono normal-case tracking-normal text-mist">
            {sessionId ? `${sessionId.slice(0, 8)}…` : 'queued'}
          </span>
        </div>
      </div>

      <p className="max-w-xs text-xs leading-relaxed text-dim">
        This panel updates automatically when processing completes.
      </p>
    </KeycapPanel>
  )
}
