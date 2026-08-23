import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { ArrowRight, LogIn, AlertCircle } from 'lucide-react'
import axios from 'axios'

import { BrandMark } from '../components/BrandMark'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { InputField } from '../components/InputField'
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
  const [isAccountConflict, setIsAccountConflict] = useState(false)

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
    setIsAccountConflict(false)
    try {
      await createAccount(values)
      navigate('/dashboard', { replace: true })
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 409) {
          setIsAccountConflict(true)
          const detail = error.response?.data?.detail
          setSubmitError(
            typeof detail === 'string'
              ? `${detail}. You can sign in directly.`
              : 'An account with this username or email already exists. You can sign in directly.'
          )
          return
        }
        const detail = error.response?.data?.detail
        if (typeof detail === 'string') {
          setSubmitError(detail)
          return
        }
      }
      setSubmitError(error instanceof Error ? error.message : 'Unable to create the account right now.')
    }
  }

  return (
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-block">
            <BrandMark />
          </div>
        </div>

        <Card variant="default" padding="none" className="p-8 space-y-6 border-[#242424] shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_16px_40px_rgba(0,0,0,0.8)]">
          <div className="border-b border-[#1C1C1C] pb-4">
            <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
              REGISTRATION // NEW_WORKSPACE
            </span>
            <h2 className="font-display text-2xl font-bold text-[#F5F5F0] mt-1">
              CREATE YOUR BEAM ACCOUNT
            </h2>
            <p className="text-xs text-[#73736F] mt-1">
              Provision a verified workspace for behavioral emotion inference.
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
            <InputField
              label="Username"
              placeholder="beam.researcher"
              autoComplete="username"
              error={errors.username?.message}
              {...register('username')}
            />

            <InputField
              label="Email address"
              type="email"
              placeholder="researcher@beam-lab.org"
              autoComplete="email"
              error={errors.email?.message}
              {...register('email')}
            />

            <InputField
              label="Password"
              type="password"
              placeholder="••••••••••••"
              autoComplete="new-password"
              error={errors.password?.message}
              {...register('password')}
            />

            <InputField
              label="Confirm Password"
              type="password"
              placeholder="••••••••••••"
              autoComplete="new-password"
              error={errors.confirmPassword?.message}
              {...register('confirmPassword')}
            />

            {submitError && (
              <div className="p-3.5 rounded-xl bg-[#1F0C0C] border border-[#5A1C1C] text-xs text-[#FF6B6B] space-y-2">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{submitError}</span>
                </div>
                {isAccountConflict && (
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-1.5 font-bold text-[#C7FF4A] hover:underline pl-6"
                  >
                    <LogIn className="h-3.5 w-3.5" /> Click here to Sign In →
                  </Link>
                )}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              fullWidth
              size="lg"
              isLoading={isSubmitting}
              rightIcon={<ArrowRight className="h-4 w-4" />}
            >
              CREATE ACCOUNT
            </Button>
          </form>

          <div className="pt-4 border-t border-[#1C1C1C] text-center text-xs text-[#73736F]">
            Already registered?{' '}
            <Link to="/login" className="font-semibold text-[#F5F5F0] hover:text-[#C7FF4A] transition-colors">
              Sign in to session →
            </Link>
          </div>
        </Card>

        <div className="text-center">
          <span className="font-mono text-[10px] text-[#555552] uppercase tracking-wider">
            Academic Research & Engineering Standard
          </span>
        </div>
      </div>
    </div>
  )
}