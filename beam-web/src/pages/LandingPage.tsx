import { Link } from 'react-router-dom'

import { BrandMark } from '../components/BrandMark'
import { Card } from '../components/Card'
import { MetricCard } from '../components/MetricCard'
import { SectionHeading } from '../components/SectionHeading'
import { buttonClassName } from '../components/buttonStyles'

const featureCards = [
  {
    title: 'Keycap surfaces',
    description: 'Every surface is tuned like a keypress: tiny lift, subtle shadow, and a fast return to rest.',
  },
  {
    title: 'Monochrome restraint',
    description: 'A pitch-black base, quiet borders, and one restrained accent keep attention on the content.',
  },
  {
    title: 'Research-first layout',
    description: 'The shell feels like a productivity instrument rather than a promotional page or admin template.',
  },
]

const stackItems = ['React', 'Vite', 'TypeScript', 'TailwindCSS', 'React Router', 'Axios', 'React Hook Form', 'Zod', 'TanStack Query']

const snapshotRows = [
  'Protected routes with JWT-aware redirects',
  'Session notes ready for explainability output',
  'Neutral typography with Geist-first hierarchy',
  'Tiny motion tuned for keycap-style interaction',
]

const stats = [
  {
    label: 'Protected routes',
    value: '5',
    description: 'Authentication and session gating across the app shell.',
  },
  {
    label: 'Surface language',
    value: 'KDS',
    description: 'Keycap Design System for cards, buttons, and input states.',
  },
  {
    label: 'Accent colors',
    value: '1',
    description: 'A single restrained accent keeps the interface disciplined.',
  },
]

export function LandingPage() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-16 px-4 py-10 sm:px-6 lg:px-8 lg:py-16">
      <section className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-8">
          <BrandMark />

          <div className="space-y-5">
            <p className="kds-keycap inline-flex rounded-[12px] px-4 py-2 text-[0.7rem] font-semibold tracking-[0.34em] text-[#b2ff7d] uppercase">
              Keycap Design System
            </p>
            <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-white sm:text-6xl lg:text-7xl">
              A research interface with the restraint of a keyboard chassis.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-white/64 sm:text-xl">
              B.E.A.M. keeps analysis, session history, and account flow inside a monochrome shell built around physical depth, tiny motion, and precision surfaces.
            </p>
          </div>

          <div className="flex flex-wrap gap-4">
            <Link to="/dashboard" className={buttonClassName('primary')}>
              Open dashboard
            </Link>
            <Link to="/login" className={buttonClassName('secondary')}>
              Sign in
            </Link>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {stats.map((stat) => (
              <MetricCard key={stat.label} title={stat.label} value={stat.value} description={stat.description} />
            ))}
          </div>
        </div>

        <Card className="space-y-6 p-8 sm:p-10">
          <p className="text-[0.7rem] font-semibold tracking-[0.34em] text-white/42 uppercase">Workspace snapshot</p>

          <div className="space-y-4">
            {snapshotRows.map((item) => (
              <div key={item} className="kds-inset rounded-[14px] px-4 py-4 text-sm text-white/70">
                {item}
              </div>
            ))}
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {[
              'Route protection with JWT-aware redirects',
              'Axios client with automatic token attachment',
              'Responsive sidebar and top navigation shell',
              'Persistent theme state for the shell',
            ].map((item) => (
              <div key={item} className="kds-inset rounded-[14px] px-4 py-4 text-sm text-white/70">
                {item}
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="space-y-8">
        <SectionHeading
          eyebrow="What ships"
          title="A shell that behaves like a product tool, not a landing page"
          description="The interface is structured around the work users actually do: signing in, checking status, reviewing sessions, and moving between analysis surfaces."
        />

        <div className="grid gap-5 md:grid-cols-3">
          {featureCards.map((feature) => (
            <Card key={feature.title} className="space-y-4">
              <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
              <p className="text-sm leading-7 text-white/62">{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <Card className="space-y-4">
          <SectionHeading eyebrow="Research Goal" title="Support explainable behavioral emotion analysis" />
          <p className="text-sm leading-7 text-white/62">
            The application presents a stable interface for reviewing the output of the broader B.E.A.M. system, which is intended to analyze emotional patterns from online behavior while keeping the experience readable and auditable.
          </p>
        </Card>

        <Card className="space-y-4">
          <SectionHeading eyebrow="Stack" title="Built with the requested frontend stack" />
          <div className="flex flex-wrap gap-3">
            {stackItems.map((stackItem) => (
              <span
                key={stackItem}
                className="kds-keycap rounded-[12px] px-4 py-2 text-sm font-medium text-white/72"
              >
                {stackItem}
              </span>
            ))}
          </div>
        </Card>
      </section>

      <section className="kds-keycap rounded-[18px] p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-[0.7rem] font-semibold tracking-[0.34em] text-white/42 uppercase">Ready to enter</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-white">Sign in to open the research console</h2>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link to="/login" className={buttonClassName('secondary')}>
              Open login
            </Link>
            <Link to="/register" className={buttonClassName('primary')}>
              Create account
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
