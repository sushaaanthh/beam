import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { InputField } from '../components/InputField'
import { SectionHeading } from '../components/SectionHeading'
import { useAuth } from '../hooks/useAuth'

const loginSchema = z.object({
  identifier: z.string().min(3, 'Enter your username or email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type LoginFormValues = z.infer<typeof loginSchema>

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      identifier: '',
      password: '',
    },
  })

  const onSubmit = async (values: LoginFormValues) => {
    setSubmitError(null)
    try {
      await login(values)
      const destination = (location.state as { from?: { pathname?: string } } | undefined)?.from?.pathname ?? '/dashboard'
      navigate(destination, { replace: true })
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Unable to sign in right now.')
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl items-center justify-center px-4 py-12 sm:px-6 lg:px-8 lg:py-20">
      <div className="grid w-full gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="hidden rounded-[2rem] border border-white/10 bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.18),_transparent_35%),linear-gradient(180deg,rgba(15,23,42,0.95),rgba(2,6,23,0.96))] p-8 text-white shadow-glow lg:flex lg:flex-col lg:justify-between">
          <div className="space-y-5">
            <p className="text-xs font-semibold tracking-[0.32em] text-cyan-300 uppercase">Secure access</p>
            <h1 className="text-4xl font-semibold tracking-tight">Sign in to B.E.A.M.</h1>
            <p className="max-w-xl text-sm leading-7 text-slate-300">
              Use your account to access the dashboard, review analysis history, update your profile, and manage settings.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              'JWT-backed session flow',
              'Protected routes and redirects',
              'FastAPI auth integration',
              'Session-aware dashboard shell',
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/10 px-4 py-4 text-sm text-slate-200 backdrop-blur">
                {item}
              </div>
            ))}
          </div>
        </div>

        <Card className="space-y-6 p-8 sm:p-10">
          <SectionHeading
            eyebrow="Login"
            title="Welcome back"
            description="Sign in with your username or email to continue into the dashboard."
          />

          <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
            <InputField
              label="Username or email"
              placeholder="researcher@beam.dev"
              autoComplete="username"
              error={errors.identifier?.message}
              {...register('identifier')}
            />

            <InputField
              label="Password"
              type="password"
              placeholder="Enter your password"
              autoComplete="current-password"
              error={errors.password?.message}
              {...register('password')}
            />

            {submitError ? <p className="text-sm font-medium text-rose-500">{submitError}</p> : null}

            <Button type="submit" className="w-full" isLoading={isSubmitting}>
              Sign in
            </Button>
          </form>

          <p className="text-sm text-slate-600 dark:text-slate-300">
            New to the platform?{' '}
            <Link to="/register" className="font-semibold text-sky-600 hover:text-sky-500 dark:text-sky-400">
              Create an account
            </Link>
          </p>
        </Card>
      </div>
    </div>
  )
}