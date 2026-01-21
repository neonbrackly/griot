'use client'

import * as React from 'react'
import Link from 'next/link'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Mail, Lock, Chrome, Building2 } from 'lucide-react'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Checkbox } from '@/components/ui/Checkbox'
import { toast } from '@/lib/hooks/useToast'
import { cn } from '@/lib/utils'

// Form validation schema
const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const { login, isLoading } = useAuth()
  const [showPassword, setShowPassword] = React.useState(false)

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login({
        email: data.email,
        password: data.password,
        rememberMe: data.rememberMe,
      })
      toast.success('Welcome back!', 'You have been logged in successfully.')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed. Please try again.'
      toast.error('Login failed', message)
    }
  }

  const handleOAuthClick = (provider: string) => {
    toast.info(`${provider} Login`, 'OAuth login is coming soon. Please use email/password.')
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
          <h1 className="text-2xl font-bold text-text-primary">Welcome to Griot</h1>
          <p className="mt-2 text-text-secondary">
            Sign in to your account to continue
          </p>
        </div>

        {/* Login Form */}
        <div className="rounded-lg border border-border-default bg-bg-secondary p-6 shadow-sm">
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

            {/* Password Input */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link
                  href="/forgot-password"
                  className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
                >
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
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
            </div>

            {/* Remember Me */}
            <div className="flex items-center space-x-2">
              <Controller
                name="rememberMe"
                control={control}
                render={({ field }) => (
                  <Checkbox
                    id="rememberMe"
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                )}
              />
              <label
                htmlFor="rememberMe"
                className="text-sm text-text-secondary cursor-pointer"
              >
                Remember me for 30 days
              </label>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full"
              loading={isLoading}
              disabled={isLoading}
            >
              Sign In
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border-default" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-bg-secondary px-2 text-text-tertiary">Or continue with</span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="grid grid-cols-3 gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => handleOAuthClick('Google')}
              disabled={isLoading}
              className="flex items-center justify-center"
            >
              <Chrome className="h-5 w-5" />
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => handleOAuthClick('Microsoft')}
              disabled={isLoading}
              className="flex items-center justify-center"
            >
              <svg className="h-5 w-5" viewBox="0 0 21 21" fill="currentColor">
                <rect x="1" y="1" width="9" height="9" />
                <rect x="11" y="1" width="9" height="9" />
                <rect x="1" y="11" width="9" height="9" />
                <rect x="11" y="11" width="9" height="9" />
              </svg>
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => handleOAuthClick('SSO')}
              disabled={isLoading}
              className="flex items-center justify-center"
            >
              <Building2 className="h-5 w-5" />
            </Button>
          </div>

          {/* Sign Up Link */}
          <p className="mt-6 text-center text-sm text-text-secondary">
            Don&apos;t have an account?{' '}
            <Link
              href="/signup"
              className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
            >
              Sign up
            </Link>
          </p>
        </div>

        {/* Dev Mode Hint */}
        <div className="mt-4 rounded-lg border border-primary-200 dark:border-primary-800 bg-primary-50 dark:bg-primary-900/20 p-3">
          <p className="text-sm text-text-secondary">
            <strong className="text-text-primary">Demo:</strong>{' '}
            Use <code className="px-1 py-0.5 bg-bg-secondary rounded text-primary-600 dark:text-primary-400">brackly@griot.com</code> / <code className="px-1 py-0.5 bg-bg-secondary rounded text-primary-600 dark:text-primary-400">melly</code> to login as admin.
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
