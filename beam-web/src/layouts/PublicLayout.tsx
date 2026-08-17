import { Link, Outlet } from 'react-router-dom'
import { BrandMark } from '../components/BrandMark'
import { Button } from '../components/Button'
import { NavigationBar } from '../components/NavigationBar'

const publicNavItems = [
  { to: '/', label: 'Overview' },
  { to: '/#features', label: 'Features' },
  { to: '/#research', label: 'Research' },
  { to: '/#architecture', label: 'Architecture' },
  { to: '/#models', label: 'Models' },
]

export function PublicLayout() {
  return (
    <div className="relative min-h-screen bg-[#050505] text-[#F5F5F0] flex flex-col selection:bg-[#C7FF4A] selection:text-[#050505]">
      <NavigationBar
        brand={<BrandMark />}
        items={publicNavItems}
        actions={(
          <div className="flex items-center gap-2.5">
            <Link to="/login">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link to="/analysis">
              <Button variant="primary" size="sm" rightIcon={<span className="font-mono text-xs">→</span>}>
                Start Analysis
              </Button>
            </Link>
          </div>
        )}
      />

      <main className="relative z-10 flex-1">
        <Outlet />
      </main>

      <footer className="relative z-10 border-t border-[#1C1C1C] bg-[#080808] py-8">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 sm:px-6 lg:px-8 md:flex-row md:items-center md:justify-between text-xs text-[#73736F]">
          <div className="flex items-center gap-3">
            <span className="font-display text-sm font-bold tracking-wider text-[#B8B8B0]">B.E.A.M.</span>
            <span>•</span>
            <span>Behavioral Emotion Analysis Model Research Framework</span>
          </div>
          <div className="flex items-center gap-6">
            <span className="font-mono text-[11px] text-[#73736F]">PyTorch • RoBERTa • Transformers • FastAPI</span>
            <span>© 2026 Academic Research Project</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
