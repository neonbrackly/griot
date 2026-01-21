'use client'

import * as React from 'react'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { toast } from '@/lib/hooks/useToast'

// Form validation schema
const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = React.useState(false)
  const [isSuccess, setIsSuccess] = React.useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: data.email }),
      })

      if (!response.ok) {
        throw new Error('Failed to send reset email')
      }

      setIsSuccess(true)
      toast.success('Email sent', 'Check your inbox for the reset link.')
    } catch (error) {
      // Always show success for security (don't reveal if email exists)
      setIsSuccess(true)
      toast.success('Email sent', 'If an account exists, you will receive a reset link.')
    } finally {
      setIsLoading(false)
    }
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
          <h1 className="text-2xl font-bold text-text-primary">Forgot your password?</h1>
          <p className="mt-2 text-text-secondary">
            No worries, we&apos;ll send you reset instructions.
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
                <h2 className="text-lg font-semibold text-text-primary">Check your email</h2>
                <p className="mt-2 text-sm text-text-secondary">
                  We sent a password reset link to your email address. The link will expire in 1 hour.
                </p>
              </div>
              <div className="pt-4 space-y-3">
                <Button
                  variant="secondary"
                  className="w-full"
                  onClick={() => setIsSuccess(false)}
                >
                  Try another email
                </Button>
                <Link href="/login">
                  <Button variant="ghost" className="w-full">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to login
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            // Form State
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Email Input */}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  leftIcon={<Mail className="h-4 w-4" />}
                  error={!!errors.email}
                  helperText={errors.email?.message}
                  disabled={isLoading}
                  {...register('email')}
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                loading={isLoading}
                disabled={isLoading}
              >
                Send Reset Link
              </Button>

              {/* Back to Login */}
              <Link href="/login">
                <Button variant="ghost" className="w-full">
                  <ArrowLeft className="h-4 w-4 mr-2" />
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
