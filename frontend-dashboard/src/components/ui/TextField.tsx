import { useId } from 'react'
import type { InputHTMLAttributes } from 'react'
import clsx from 'clsx'

export interface TextFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string
  description?: string
  error?: string
}

export function TextField({ label, description, error, className, ...props }: TextFieldProps) {
  const id = useId()
  const descriptionId = description ? `${id}-description` : undefined
  const errorId = error ? `${id}-error` : undefined

  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-slate-700 dark:text-slate-200">
        {label}
      </label>
      {description && (
        <p id={descriptionId} className="text-xs text-slate-500 dark:text-slate-400">
          {description}
        </p>
      )}
      <input
        id={id}
        aria-describedby={clsx(descriptionId, errorId) || undefined}
        aria-invalid={error ? true : undefined}
        className={clsx(
          'w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-900 shadow-sm transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
          'dark:bg-slate-800 dark:text-slate-50',
          error ? 'border-red-400 dark:border-red-500' : 'border-slate-300 dark:border-slate-700',
          className,
        )}
        {...props}
      />
      {error && (
        <p id={errorId} role="alert" className="text-xs text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
    </div>
  )
}
