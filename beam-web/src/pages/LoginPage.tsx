import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { ArrowRight, AlertCircle, CheckCircle2, KeyRound, ArrowLeft, Mail, ShieldCheck, RefreshCw } from 'lucide-react'
import axios from 'axios'

import { BrandMark } from '../components/BrandMark'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { InputField } from '../components/InputField'
import { describeApiError } from '../services/api/errors'
import { useAuth } from '../hooks/useAuth'
import { sendOtpRequest, resetPasswordWithOtpRequest } from '../services/api/auth'

const loginSchema = z.object({
  identifier: z.string().min(3, 'Enter your username or email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

const resetSchema = z
  .object({
    identifier: z.string().min(3, 'Enter your username or email'),
    otp: z.string().min(4, 'Enter the verification OTP code').max(8, 'Invalid OTP code'),
    newPassword: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string().min(8, 'Confirm your new password'),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

type LoginFormValues = z.infer<typeof loginSchema>
type ResetFormValues = z.infer<typeof resetSchema>

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [submitError, setSubmitError] = useState<string | null>(null)
  
  // Password Recovery & OTP State
  const [isResetMode, setIsResetMode] = useState(false)
  const [resetSuccess, setResetSuccess] = useState<string | null>(null)
  const [resetError, setResetError] = useState<string | null>(null)
  const [otpSentMessage, setOtpSentMessage] = useState<string | null>(null)
  const [activeOtpCode, setActiveOtpCode] = useState<string | null>(null)
  const [isSendingOtp, setIsSendingOtp] = useState(false)

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

  const {
    register: registerReset,
    handleSubmit: handleSubmitReset,
    setValue: setResetValue,
    watch: watchReset,
    formState: { errors: resetErrors, isSubmitting: isResetSubmitting },
    reset: resetResetForm,
  } = useForm<ResetFormValues>({
    resolver: zodResolver(resetSchema),
    defaultValues: {
      identifier: '',
      otp: '',
      newPassword: '',
      confirmPassword: '',
    },
  })

  const currentIdentifier = watchReset('identifier')

  const onSubmit = async (values: LoginFormValues) => {
    setSubmitError(null)
    try {
      await login(values)
      const destination = (location.state as { from?: { pathname?: string } } | undefined)?.from?.pathname ?? '/dashboard'
      navigate(destination, { replace: true })
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          setSubmitError('Incorrect username, email, or password. Please try again.')
          return
        }
        const detail = error.response?.data?.detail
        if (typeof detail === 'string') {
          setSubmitError(detail)
          return
        }
      }
      setSubmitError(describeApiError(error, 'Unable to authenticate session.'))
    }
  }

  const handleSendOtp = async () => {
    if (!currentIdentifier || currentIdentifier.trim().length < 3) {
      setResetError('Please enter your username or registered email first.')
      return
    }

    setResetError(null)
    setIsSendingOtp(true)
    try {
      const res = await sendOtpRequest(currentIdentifier.trim())
      setOtpSentMessage(res.message)
      if (res.otp) {
        setActiveOtpCode(res.otp)
        setResetValue('otp', res.otp) // Pre-fill for instantaneous seamless experience
      }
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail
        if (typeof detail === 'string') {
          setResetError(detail)
          return
        }
      }
      setResetError('Unable to generate verification OTP. Please verify your account.')
    } finally {
      setIsSendingOtp(false)
    }
  }

  const onResetSubmit = async (values: ResetFormValues) => {
    setResetError(null)
    setResetSuccess(null)
    try {
      const msg = await resetPasswordWithOtpRequest(values.identifier.trim(), values.otp.trim(), values.newPassword)
      setResetSuccess(msg || 'Password updated successfully! You can now sign in with your new password.')
      resetResetForm()
      setActiveOtpCode(null)
      setOtpSentMessage(null)
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail
        if (typeof detail === 'string') {
          setResetError(detail)
          return
        }
      }
      setResetError(describeApiError(error, 'Failed to verify OTP or reset password.'))
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
          {isResetMode ? (
            /* Reset Password View with OTP */
            <>
              <div className="border-b border-[#1C1C1C] pb-4">
                <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
                  CREDENTIALS // OTP VERIFICATION
                </span>
                <h2 className="font-display text-2xl font-bold text-[#F5F5F0] mt-1 flex items-center gap-2">
                  <KeyRound className="h-5 w-5 text-[#C7FF4A]" /> RESET PASSWORD
                </h2>
                <p className="text-xs text-[#73736F] mt-1">
                  Verify your identity via 6-digit OTP code to update your password.
                </p>
              </div>

              {resetSuccess ? (
                <div className="space-y-4 py-2">
                  <div className="p-4 rounded-lg bg-[#0C1F10] border border-[#1C5A28] text-xs text-[#A8FFB2] flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 shrink-0 text-[#C7FF4A] mt-0.5" />
                    <div className="space-y-1">
                      <p className="font-semibold text-sm text-[#F5F5F0]">Password Updated Successfully!</p>
                      <p>{resetSuccess}</p>
                    </div>
                  </div>

                  <Button
                    type="button"
                    variant="primary"
                    fullWidth
                    size="lg"
                    onClick={() => {
                      setIsResetMode(false)
                      setResetSuccess(null)
                    }}
                    rightIcon={<ArrowRight className="h-4 w-4" />}
                  >
                    BACK TO SIGN IN
                  </Button>
                </div>
              ) : (
                <form className="space-y-4" onSubmit={handleSubmitReset(onResetSubmit)}>
                  {/* Identifier & Send OTP Action */}
                  <div className="space-y-1.5">
                    <InputField
                      label="Username or Registered Email"
                      placeholder="e.g. sushanth_2005 or email"
                      autoComplete="username"
                      error={resetErrors.identifier?.message}
                      {...registerReset('identifier')}
                    />

                    <div className="flex items-center justify-between pt-0.5">
                      <button
                        type="button"
                        onClick={handleSendOtp}
                        disabled={isSendingOtp}
                        className="text-xs font-mono text-[#C7FF4A] hover:underline flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                      >
                        {isSendingOtp ? (
                          <>
                            <RefreshCw className="h-3 w-3 animate-spin" /> Generating OTP...
                          </>
                        ) : (
                          <>
                            <Mail className="h-3 w-3" /> Request OTP Code
                          </>
                        )}
                      </button>

                      {otpSentMessage && (
                        <span className="text-[11px] font-mono text-[#C7FF4A] flex items-center gap-1">
                          <ShieldCheck className="h-3 w-3" /> OTP Dispatched
                        </span>
                      )}
                    </div>
                  </div>

                  {/* OTP Notification Banner */}
                  {otpSentMessage && (
                    <div className="p-3 bg-[#111A11] border border-[#234224] rounded-lg text-xs space-y-1">
                      <div className="flex items-center gap-1.5 text-[#C7FF4A] font-semibold">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        <span>{otpSentMessage}</span>
                      </div>
                      {activeOtpCode && (
                        <div className="flex items-center justify-between font-mono text-[11px] text-[#A0A09A] pt-1">
                          <span>Verification Code:</span>
                          <span className="px-2 py-0.5 rounded bg-[#1C2E1D] text-[#C7FF4A] font-bold text-xs tracking-widest border border-[#2B4B2D]">
                            {activeOtpCode}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* OTP Input */}
                  <InputField
                    label="6-Digit Verification OTP"
                    placeholder="Enter 6-digit code (e.g. 123456)"
                    error={resetErrors.otp?.message}
                    {...registerReset('otp')}
                  />

                  {/* New Password */}
                  <InputField
                    label="New Password"
                    type="password"
                    placeholder="••••••••••••"
                    autoComplete="new-password"
                    error={resetErrors.newPassword?.message}
                    {...registerReset('newPassword')}
                  />

                  {/* Confirm Password */}
                  <InputField
                    label="Confirm New Password"
                    type="password"
                    placeholder="••••••••••••"
                    autoComplete="new-password"
                    error={resetErrors.confirmPassword?.message}
                    {...registerReset('confirmPassword')}
                  />

                  {resetError && (
                    <div className="p-3 rounded-lg bg-[#1F0C0C] border border-[#5A1C1C] text-xs text-[#FF6B6B] flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 shrink-0" />
                      <span>{resetError}</span>
                    </div>
                  )}

                  <div className="flex items-center gap-3 pt-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="lg"
                      onClick={() => {
                        setIsResetMode(false)
                        setResetError(null)
                        setOtpSentMessage(null)
                        setActiveOtpCode(null)
                      }}
                      className="border-[#2E2E2E] text-xs font-mono"
                      leftIcon={<ArrowLeft className="h-3.5 w-3.5" />}
                    >
                      CANCEL
                    </Button>

                    <Button
                      type="submit"
                      variant="primary"
                      className="flex-1"
                      size="lg"
                      isLoading={isResetSubmitting}
                      rightIcon={<ArrowRight className="h-4 w-4" />}
                    >
                      VERIFY & RESET
                    </Button>
                  </div>
                </form>
              )}
            </>
          ) : (
            /* Regular Sign In View */
            <>
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
                  <button
                    type="button"
                    onClick={() => {
                      setIsResetMode(true)
                      setSubmitError(null)
                      setResetError(null)
                    }}
                    className="text-[#73736F] hover:text-[#C7FF4A] transition-colors cursor-pointer"
                  >
                    Forgot password?
                  </button>
                </div>

                {submitError && (
                  <div className="p-3 rounded-lg bg-[#1F0C0C] border border-[#5A1C1C] text-xs text-[#FF6B6B] flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 shrink-0" />
                    <span>{submitError}</span>
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
            </>
          )}
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