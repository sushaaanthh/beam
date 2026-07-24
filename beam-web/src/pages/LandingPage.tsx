import { Link } from 'react-router-dom'

import { BrandMark } from '../components/BrandMark'
import { Card } from '../components/Card'
import { SectionHeading } from '../components/SectionHeading'
import { buttonClassName } from '../components/buttonStyles'

const featureCards = [
  {
    title: 'Behavioral insight workspace',
    description: 'A clean interface for tracking analysis sessions, reviewing model output, and understanding user behavior patterns.',
  },
  {
    title: 'JWT-secured authentication',
    description: 'Login and session flow are wired to the FastAPI auth endpoints with protected dashboard routing.',
  },
  {
    title: 'Responsive SaaS layout',
    description: 'A dashboard shell designed for desktop and mobile with a sidebar, top navigation, and card-based content regions.',
  },
]

const stackItems = ['React', 'Vite', 'TypeScript', 'TailwindCSS', 'React Router', 'Axios', 'React Hook Form', 'Zod', 'TanStack Query']

export function LandingPage() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-16 px-4 py-10 sm:px-6 lg:px-8 lg:py-16">
      <section className="grid items-center gap-12 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-8">
          <BrandMark />

          <div className="space-y-5">
            <p className="inline-flex rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-xs font-semibold tracking-[0.3em] text-cyan-700 uppercase dark:text-cyan-300">
              Behavioral Emotion Analysis Model
            </p>
            <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-slate-950 sm:text-6xl lg:text-7xl dark:text-white">
              B.E.A.M.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-600 sm:text-xl dark:text-slate-300">
              A modern frontend shell for analyzing behavioral emotion signals, managing authenticated research workflows, and preparing the platform for production usage.
            </p>
          </div>

          <div className="flex flex-wrap gap-4">
            <Link to="/register" className={buttonClassName('primary')}>
              Get started
            </Link>
            <Link to="/login" className={buttonClassName('secondary')}>
              Sign in
            </Link>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {[
              { label: 'Protected routes', value: '5' },
              { label: 'Core pages', value: '9' },
              { label: 'UI focus', value: 'SaaS shell' },
            ].map((stat) => (
              <Card key={stat.label} className="p-5">
                <p className="text-sm text-slate-500 dark:text-slate-400">{stat.label}</p>
                <p className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">{stat.value}</p>
              </Card>
            ))}
          </div>
        </div>

        <Card className="relative overflow-hidden p-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.18),_transparent_35%),linear-gradient(180deg,rgba(15,23,42,0.05),rgba(15,23,42,0.02))] dark:bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.2),_transparent_35%),linear-gradient(180deg,rgba(148,163,184,0.06),rgba(15,23,42,0.22))]" />
          <div className="relative space-y-6 p-8 sm:p-10">
            <p className="text-xs font-semibold tracking-[0.32em] text-cyan-700 uppercase dark:text-cyan-300">Platform snapshot</p>
            <h2 className="text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">Secure research workspace with a polished dashboard feel</h2>
            <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
              The frontend is structured for authenticated analysis sessions, history review, profile management, and future AI-powered workflows without bringing in charting or model execution yet.
            </p>

            <div className="grid gap-4 sm:grid-cols-2">
              {[
                'Route protection with JWT-aware redirects',
                'Axios client with automatic token attachment',
                'Responsive sidebar and top navigation shell',
                'Dark mode support with persistent theme state',
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/60 px-4 py-4 text-sm text-slate-700 backdrop-blur dark:bg-slate-950/50 dark:text-slate-200">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </Card>
      </section>

      <section className="space-y-8">
        <SectionHeading
          eyebrow="Features"
          title="Designed to feel like a real product from the first screen"
          description="The shell focuses on the operations users will actually perform: signing in, reviewing sessions, checking recent work, and navigating a stable dashboard interface."
        />

        <div className="grid gap-5 md:grid-cols-3">
          {featureCards.map((feature) => (
            <Card key={feature.title} className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-950 dark:text-white">{feature.title}</h3>
              <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <SectionHeading
          eyebrow="Technology Stack"
          title="Built with the requested frontend stack"
          description="The project uses React, Vite, TypeScript, TailwindCSS, React Router, Axios, React Hook Form, Zod, and TanStack Query."
        />
        <Card className="flex flex-wrap gap-3">
          {stackItems.map((stackItem) => (
            <span
              key={stackItem}
              className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
            >
              {stackItem}
            </span>
          ))}
        </Card>
      </section>

      <section className="grid gap-8 lg:grid-cols-2">
        <Card className="space-y-4">
          <SectionHeading eyebrow="Research Goal" title="Support explainable behavioral emotion analysis" />
          <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
            The application presents a stable interface for reviewing the output of the broader B.E.A.M. system, which is intended to analyze emotional patterns from online behavior while keeping the experience readable and auditable.
          </p>
        </Card>

        <Card className="space-y-4">
          <SectionHeading eyebrow="About" title="A product-grade shell for the wider platform" />
          <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
            This frontend does not run AI models or chart pipelines. It gives the project a polished surface for authentication, navigation, and future dashboard growth while keeping the architecture easy to extend.
          </p>
        </Card>
      </section>

      <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-glow dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold tracking-[0.32em] text-cyan-700 uppercase dark:text-cyan-300">Ready to explore</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">Sign in to open the dashboard shell</h2>
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