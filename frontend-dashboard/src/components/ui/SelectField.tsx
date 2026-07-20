import { useId } from 'react'
import type { SelectHTMLAttributes } from 'react'
import clsx from 'clsx'

export interface SelectOption {
  value: string
  label: string
}

export interface SelectFieldProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'id'> {
  label: string
  description?: string
  options: SelectOption[]
}

export function SelectField({
  label,
  description,
  options,
  className,
  ...props
}: SelectFieldProps) {
  const id = useId()
  const descriptionId = description ? `${id}-description` : undefined

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
      <select
        id={id}
        aria-describedby={descriptionId}
        className={clsx(
          'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
          'dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50',
          className,
        )}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}
