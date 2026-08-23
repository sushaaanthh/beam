import { Link } from 'react-router-dom'
import { Container } from './Container'
import { StatusIndicator } from './StatusIndicator'
import { TechnicalLabel } from './TechnicalLabel'

const pipelineStages = ['Collect', 'Clean', 'Analyze', 'Infer', 'Explain']

export function Footer() {
  return (
    <footer className="relative z-10 border-t border-line-subtle bg-deep">
      <Container className="flex flex-col gap-10 py-12">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr]">
          {/* Brand */}
          <div className="space-y-3">
            <div className="flex items-baseline gap-3">
              <span className="font-display text-xl font-semibold tracking-[0.08em] text-chalk">
                B.E.A.M.
              </span>
              <span className="text-[9px] font-medium uppercase tracking-[0.22em] text-dim">
                Behavioral Emotion Analysis Model
              </span>
            </div>
            <p className="max-w-sm text-xs leading-relaxed text-dim">
              An explainable deep learning framework for analyzing emotional states
              and behavioral signals in online textual data.
            </p>
            <StatusIndicator label="System Nominal" tone="operational" />
          </div>

          {/* Pipeline */}
          <nav aria-label="Research pipeline" className="space-y-3">
            <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-dim">
              Pipeline
            </p>
            <ul className="space-y-2 text-xs text-mist">
              {pipelineStages.map((stage, i) => (
                <li key={stage} className="flex items-center gap-2.5">
                  <span className="font-ui text-[10px] text-dim" aria-hidden="true">
                    0{i + 1}
                  </span>
                  <span className="uppercase tracking-[0.08em]">{stage}</span>
                </li>
              ))}
            </ul>
          </nav>

          {/* Stack + docs */}
          <div className="space-y-3">
            <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-dim">
              Research Stack
            </p>
            <div className="flex flex-wrap gap-2">
              {['PyTorch', 'RoBERTa', 'FastAPI', 'React'].map((tech) => (
                <TechnicalLabel key={tech}>{tech}</TechnicalLabel>
              ))}
            </div>
            <p className="pt-2 text-xs leading-relaxed text-dim">
              Full documentation lives in the repository
              <span className="ml-1 font-medium text-mist">/docs</span> directory.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 border-t border-line-subtle pt-6 text-[11px] text-dim md:flex-row md:items-center md:justify-between">
          <span>© 2026 Academic Research Project</span>
          <Link to="/login" className="transition-colors duration-150 hover:text-chalk">
            Sign In
          </Link>
        </div>
      </Container>
    </footer>
  )
}
