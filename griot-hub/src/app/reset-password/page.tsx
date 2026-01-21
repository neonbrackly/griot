'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Lock, Eye, EyeOff, CheckCircle, Check, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { toast } from '@/lib/hooks/useToast'
import { cn } from '@/lib/utils'

// Password strength calculation
function calculatePasswordStrength(password: string): {
  score: number
  label: 'weak' | 'medium' | 'strong'
  requirements: { label: string; met: boolean }[]
} {
  const requirements = [
    { label: 'At least 8 characters', met: password.length >= 8 },
    { label: 'Contains uppercase letter', met: /[A-Z]/.test(password) },
    { label: 'Contains lowercase letter', met: /[a-z]/.test(password) },
    { label: 'Contains number', met: /[0-9]/.test(password) },
    { label: 'Contains special character', met: /[!@#$%^&*(),.?":{}|<>]/.test(password) },
  ]

  const metCount = requirements.filter((r) => r.met).length
  const score = (metCount / requirements.length) * 100

  let label: 'weak' | 'medium' | 'strong' = 'weak'
  if (score >= 80) label = 'strong'
  else if (score >= 60) label = 'medium'

  return { score, label, requirements }
}

// Form validation schema
const resetPasswordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

export default function ResetPasswordPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [isLoading, setIsLoading] = React.useState(false)
  const [isSuccess, setIsSuccess] = React.useState(false)
  const [showPassword, setShowPassword] = React.useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  })

  const password = watch('password')
  const passwordStrength = React.useMemo(
    () => calculatePasswordStrength(password || ''),
    [password]
  )

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      toast.error('Invalid link', 'Reset token is missing. Please request a new reset link.')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          password: data.password,
          confirmPassword: data.confirmPassword,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error?.message || 'Failed to reset password')
      }

      setIsSuccess(true)
      toast.success('Password reset!', 'Your password has been reset successfully.')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to reset password'
      toast.error('Reset failed', message)
    } finally {
      setIsLoading(false)
    }
  }

  // If no token, show error
  if (!token && !isSuccess) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg-primary px-4">
        <div className="w-full max-w-md">
          <div className="rounded-lg border border-error-200 dark:border-error-800 bg-error-50 dark:bg-error-900/20 p-6 text-center">
            <h1 className="text-lg font-semibold text-text-primary">Invalid Reset Link</h1>
            <p className="mt-2 text-sm text-text-secondary">
              This password reset link is invalid or has expired. Please request a new one.
            </p>
            <Link href="/forgot-password">
              <Button className="mt-4">Request New Link</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-primary px-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-xl bg-primary-600">
            <svg
              className="h-8 w-8 text-white"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-text-primary">Reset your password</h1>
          <p className="mt-2 text-text-secondary">
            Choose a new password for your account.
          </p>
        </div>

        {/* Form Card */}
        <div className="rounded-lg border border-border-default bg-bg-secondary p-6 shadow-sm">
          {isSuccess ? (
            // Success State
            <div className="text-center space-y-4">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-success-100 dark:bg-success-900/30">
                <CheckCircle className="h-6 w-6 text-success-600 dark:text-success-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-text-primary">Password reset successful</h2>
                <p className="mt-2 text-sm text-text-secondary">
                  Your password has been reset. You can now log in with your new password.
                </p>
              </div>
              <div className="pt-4">
                <Link href="/login">
                  <Button className="w-full">Continue to Login</Button>
                </Link>
              </div>
            </div>
          ) : (
            // Form State
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* New Password Input */}
              <div className="space-y-2">
                <Label htmlFor="password">New Password</Label>
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter new password"
                  leftIcon={<Lock className="h-4 w-4" />}
                  rightIcon={
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="hover:text-text-primary transition-colors"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  }
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  disabled={isLoading}
                  {...register('password')}
                />

                {/* Password Strength Indicator */}
                {password && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
                        <div
                          className={cn(
                            'h-full transition-all duration-300',
                            passwordStrength.label === 'weak' && 'bg-error-500',
                            passwordStrength.label === 'medium' && 'bg-warning-500',
                            passwordStrength.label === 'strong' && 'bg-success-500'
                          )}
                          style={{ width: `${passwordStrength.score}%` }}
                        />
                      </div>
                      <span
                        className={cn(
                          'text-xs font-medium capitalize',
                          passwordStrength.label === 'weak' && 'text-error-500',
                          passwordStrength.label === 'medium' && 'text-warning-500',
                          passwordStrength.label === 'strong' && 'text-success-500'
                        )}
                      >
                        {passwordStrength.label}
                      </span>
                    </div>
                    <ul className="space-y-1">
                      {passwordStrength.requirements.map((req, i) => (
                        <li
                          key={i}
                          className={cn(
                            'flex items-center gap-1.5 text-xs',
                            req.met ? 'text-success-600 dark:text-success-400' : 'text-text-tertiary'
                          )}
                        >
                          {req.met ? (
                            <Check className="h-3 w-3" />
                          ) : (
                            <X className="h-3 w-3" />
                          )}
                          {req.label}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Confirm Password Input */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Confirm your password"
                  leftIcon={<Lock className="h-4 w-4" />}
                  rightIcon={
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="hover:text-text-primary transition-colors"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  }
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword?.message}
                  disabled={isLoading}
                  {...register('confirmPassword')}
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                loading={isLoading}
                disabled={isLoading}
              >
                Reset Password
              </Button>

              {/* Back to Login */}
              <Link href="/login">
                <Button variant="ghost" className="w-full">
                  Back to login
                </Button>
              </Link>
            </form>
          )}
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-sm text-text-tertiary">
          Griot Data Contract Management System
        </p>
      </div>
    </div>
  )
}
