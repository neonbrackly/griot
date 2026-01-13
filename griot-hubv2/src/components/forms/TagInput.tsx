'use client'

import * as React from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'

interface TagInputProps {
  value: string[]
  onChange: (tags: string[]) => void
  suggestions?: string[]
  placeholder?: string
  maxTags?: number
  disabled?: boolean
  error?: boolean
  className?: string
}

export function TagInput({
  value,
  onChange,
  suggestions = [],
  placeholder = 'Add a tag...',
  maxTags,
  disabled,
  error,
  className,
}: TagInputProps) {
  const [inputValue, setInputValue] = React.useState('')
  const [showSuggestions, setShowSuggestions] = React.useState(false)
  const inputRef = React.useRef<HTMLInputElement>(null)

  const filteredSuggestions = React.useMemo(() => {
    if (!inputValue) return suggestions.filter((s) => !value.includes(s))
    return suggestions.filter(
      (s) =>
        s.toLowerCase().includes(inputValue.toLowerCase()) && !value.includes(s)
    )
  }, [inputValue, suggestions, value])

  const addTag = (tag: string) => {
    const trimmedTag = tag.trim().toLowerCase()
    if (!trimmedTag) return
    if (value.includes(trimmedTag)) return
    if (maxTags && value.length >= maxTags) return

    onChange([...value, trimmedTag])
    setInputValue('')
  }

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue) {
      e.preventDefault()
      addTag(inputValue)
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1])
    } else if (e.key === 'Escape') {
      setShowSuggestions(false)
    }
  }

  return (
    <div className={cn('relative', className)}>
      <div
        className={cn(
          'flex flex-wrap gap-2 p-2 min-h-[42px] rounded-lg border bg-bg-primary',
          'focus-within:ring-2 focus-within:ring-border-focus focus-within:ring-offset-2 focus-within:ring-offset-bg-primary',
          error ? 'border-error-500' : 'border-border-default',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onClick={() => inputRef.current?.focus()}
      >
        {value.map((tag) => (
          <Badge
            key={tag}
            variant="secondary"
            size="sm"
            className="gap-1 pr-1"
          >
            {tag}
            {!disabled && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  removeTag(tag)
                }}
                className="rounded-full p-0.5 hover:bg-bg-hover"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </Badge>
        ))}

        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value)
            setShowSuggestions(true)
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={value.length === 0 ? placeholder : ''}
          disabled={disabled || (maxTags !== undefined && value.length >= maxTags)}
          className={cn(
            'flex-1 min-w-[100px] bg-transparent border-none outline-none text-sm',
            'placeholder:text-text-tertiary'
          )}
        />
      </div>

      {/* Suggestions dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && (
        <div className="absolute z-dropdown mt-1 w-full bg-bg-secondary border border-border-default rounded-lg shadow-lg overflow-hidden">
          <div className="max-h-40 overflow-y-auto p-1">
            {filteredSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault()
                  addTag(suggestion)
                }}
                className={cn(
                  'w-full px-3 py-2 text-left text-sm rounded-md',
                  'hover:bg-bg-hover transition-colors'
                )}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Tag count */}
      {maxTags && (
        <p className="mt-1.5 text-xs text-text-tertiary">
          {value.length}/{maxTags} tags
        </p>
      )}
    </div>
  )
}
