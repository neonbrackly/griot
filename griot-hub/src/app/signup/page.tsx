'use client'

import * as React from 'react'
import Link from 'next/link'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Mail, Lock, User, Chrome, Check, X } from 'lucide-react'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Checkbox } from '@/components/ui/Checkbox'
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
const signupSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
  acceptTerms: z.boolean().refine((val) => val === true, {
    message: 'You must accept the terms and conditions',
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

type SignupFormData = z.infer<typeof signupSchema>

export default function SignupPage() {
  const { signup, isLoading } = useAuth()
  const [showPassword, setShowPassword] = React.useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false)

  const {
    register,
    handleSubmit,
    watch,
    control,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false,
    },
  })

  const password = watch('password')
  const passwordStrength = React.useMemo(
    () => calculatePasswordStrength(password || ''),
    [password]
  )

  const onSubmit = async (data: SignupFormData) => {
    try {
      await signup({
        name: data.name,
        email: data.email,
        password: data.password,
        confirmPassword: data.confirmPassword,
        acceptTerms: data.acceptTerms,
      })
      toast.success('Account created!', 'Welcome to Griot.')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Signup failed. Please try again.'
      toast.error('Signup failed', message)
    }
  }

  const handleOAuthClick = (provider: string) => {
    toast.info(`${provider} Signup`, 'OAuth signup is coming soon. Please use email/password.')
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-primary px-4 py-8">
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
          <h1 className="text-2xl font-bold text-text-primary">Create your account</h1>
          <p className="mt-2 text-text-secondary">
            Get started with Griot today
          </p>
        </div>

        {/* Signup Form */}
        <div className="rounded-lg border border-border-default bg-bg-secondary p-6 shadow-sm">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Name Input */}
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                leftIcon={<User className="h-4 w-4" />}
                error={!!errors.name}
                helperText={errors.name?.message}
                disabled={isLoading}
                {...register('name')}
              />
            </div>

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

            {/* Password Input */}
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a password"
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
              <Label htmlFor="confirmPassword">Confirm Password</Label>
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

            {/* Terms and Conditions */}
            <div className="space-y-1">
              <div className="flex items-start space-x-2">
                <Controller
                  name="acceptTerms"
                  control={control}
                  render={({ field }) => (
                    <Checkbox
                      id="acceptTerms"
                      className="mt-0.5"
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  )}
                />
                <label
                  htmlFor="acceptTerms"
                  className="text-sm text-text-secondary cursor-pointer"
                >
                  I agree to the{' '}
                  <Link href="#" className="text-primary-600 hover:text-primary-700 dark:text-primary-400">
                    Terms of Service
                  </Link>{' '}
                  and{' '}
                  <Link href="#" className="text-primary-600 hover:text-primary-700 dark:text-primary-400">
                    Privacy Policy
                  </Link>
                </label>
              </div>
              {errors.acceptTerms && (
                <p className="text-xs text-error-500">{errors.acceptTerms.message}</p>
              )}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full"
              loading={isLoading}
              disabled={isLoading}
            >
              Create Account
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border-default" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-bg-secondary px-2 text-text-tertiary">Or sign up with</span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => handleOAuthClick('Google')}
              disabled={isLoading}
              className="flex items-center justify-center gap-2"
            >
              <Chrome className="h-5 w-5" />
              <span>Google</span>
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => handleOAuthClick('Microsoft')}
              disabled={isLoading}
              className="flex items-center justify-center gap-2"
            >
              <svg className="h-5 w-5" viewBox="0 0 21 21" fill="currentColor">
                <rect x="1" y="1" width="9" height="9" />
                <rect x="11" y="1" width="9" height="9" />
                <rect x="1" y="11" width="9" height="9" />
                <rect x="11" y="11" width="9" height="9" />
              </svg>
              <span>Microsoft</span>
            </Button>
          </div>

          {/* Login Link */}
          <p className="mt-6 text-center text-sm text-text-secondary">
            Already have an account?{' '}
            <Link
              href="/login"
              className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
            >
              Sign in
            </Link>
          </p>
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-sm text-text-tertiary">
          Griot Data Contract Management System
        </p>
      </div>
    </div>
  )
}
