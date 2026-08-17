import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { ArrowRight, Lock, User, ShieldCheck } from 'lucide-react'

import { BrandMark } from '../components/BrandMark'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { InputField } from '../components/InputField'
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
      setSubmitError(error instanceof Error ? error.message : 'Unable to authenticate session.')
    }
  }

  return (
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Centered Brand Icon */}
        <div className="text-center space-y-2">
          <div className="inline-block">
            <BrandMark />
          </div>
        </div>

        {/* Tactile Keycap Authentication Card */}
        <Card variant="default" padding="none" className="p-8 space-y-6 border-[#242424] shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_16px_40px_rgba(0,0,0,0.8)]">
          <div className="border-b border-[#1C1C1C] pb-4">
            <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
              AUTHENTICATION // SESSION_INIT
            </span>
            <h2 className="font-display text-2xl font-bold text-[#F5F5F0] mt-1">
              WELCOME BACK
            </h2>
            <p className="text-xs text-[#73736F] mt-1">
              Sign in to access your behavioral analysis workspace.
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
            <InputField
              label="Username or Email"
              placeholder="researcher@beam-lab.org"
              autoComplete="username"
              error={errors.identifier?.message}
              {...register('identifier')}
            />

            <InputField
              label="Password"
              type="password"
              placeholder="••••••••••••"
              autoComplete="current-password"
              error={errors.password?.message}
              {...register('password')}
            />

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-[#73736F] hover:text-[#B8B8B0]">
                <input
                  type="checkbox"
                  className="h-3.5 w-3.5 accent-[#C7FF4A] rounded bg-[#0A0A0A] border-[#222222]"
                />
                <span>Remember session</span>
              </label>
              <a href="#reset" className="text-[#73736F] hover:text-[#C7FF4A] transition-colors">
                Forgot password?
              </a>
            </div>

            {submitError && (
              <div className="p-3 rounded-lg bg-[#1F0C0C] border border-[#5A1C1C] text-xs text-[#FF6B6B]">
                {submitError}
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
              SIGN IN
            </Button>
          </form>

          <div className="pt-4 border-t border-[#1C1C1C] text-center text-xs text-[#73736F]">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-[#F5F5F0] hover:text-[#C7FF4A] transition-colors">
              Create research account →
            </Link>
          </div>
        </Card>

        <div className="text-center">
          <span className="font-mono text-[10px] text-[#555552] uppercase tracking-wider">
            Protected with 256-bit Token Encryption
          </span>
        </div>
      </div>
    </div>
  )
}