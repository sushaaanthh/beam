import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { InputField } from '../components/InputField'
import { SectionHeading } from '../components/SectionHeading'
import { useAuth } from '../hooks/useAuth'

const registerSchema = z
  .object({
    username: z.string().min(3, 'Username must be at least 3 characters').max(50),
    email: z.string().email('Enter a valid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string().min(8, 'Confirm your password'),
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

type RegisterFormValues = z.infer<typeof registerSchema>

export function RegisterPage() {
  const navigate = useNavigate()
  const { register: createAccount } = useAuth()
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  })

  const onSubmit = async (values: RegisterFormValues) => {
    setSubmitError(null)
    try {
      await createAccount(values)
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Unable to create the account right now.')
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl items-center justify-center px-4 py-12 sm:px-6 lg:px-8 lg:py-20">
      <div className="grid w-full gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <Card className="space-y-6 p-8 sm:p-10">
          <SectionHeading
            eyebrow="Register"
            title="Create your research account"
            description="Use a professional workspace for future behavioral analysis sessions."
          />

          <form className="grid gap-5" onSubmit={handleSubmit(onSubmit)}>
            <InputField
              label="Username"
              placeholder="beam.research"
              autoComplete="username"
              error={errors.username?.message}
              {...register('username')}
            />

            <InputField
              label="Email address"
              type="email"
              placeholder="researcher@beam.dev"
              autoComplete="email"
              error={errors.email?.message}
              {...register('email')}
            />

            <InputField
              label="Password"
              type="password"
              placeholder="Create a strong password"
              autoComplete="new-password"
              error={errors.password?.message}
              {...register('password')}
            />

            <InputField
              label="Confirm password"
              type="password"
              placeholder="Repeat the password"
              autoComplete="new-password"
              error={errors.confirmPassword?.message}
              {...register('confirmPassword')}
            />

            {submitError ? <p className="text-sm font-medium text-rose-500">{submitError}</p> : null}

            <Button type="submit" className="w-full" isLoading={isSubmitting}>
              Create account
            </Button>
          </form>

          <p className="text-sm text-white/62">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-white/82 hover:text-white">
              Sign in
            </Link>
          </p>
        </Card>

        <Card className="space-y-6 p-8 text-white">
          <div className="space-y-4">
            <p className="text-[0.7rem] font-semibold tracking-[0.34em] text-white/42 uppercase">Why register?</p>
            <h1 className="text-4xl font-semibold tracking-tight">A clean starting point for the full B.E.A.M. experience</h1>
            <p className="text-sm leading-7 text-white/62">
              The frontend is intentionally focused on structure and workflow readiness, so the next phase can plug in analysis sessions, explainability views, and reporting without redesigning the interface.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              'Quick account creation',
              'JWT session handling',
              'Responsive form validation',
              'Ready for dashboard access',
            ].map((item) => (
              <div key={item} className="rounded-[1rem] border border-white/10 bg-white/4 px-4 py-4 text-sm text-white/72">
                {item}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}