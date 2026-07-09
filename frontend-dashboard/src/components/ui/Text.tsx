import clsx from 'clsx'
import type { HTMLAttributes } from 'react'

export type TextVariant = 'body' | 'muted' | 'caption'

export interface TextProps extends HTMLAttributes<HTMLParagraphElement> {
  variant?: TextVariant
}

const VARIANT_CLASSES: Record<TextVariant, string> = {
  body: 'text-sm text-slate-700 dark:text-slate-300',
  muted: 'text-sm text-slate-500 dark:text-slate-400',
  caption: 'text-xs text-slate-500 dark:text-slate-400',
}

export function Text({ variant = 'body', className, children, ...props }: TextProps) {
  return (
    <p className={clsx(VARIANT_CLASSES[variant], className)} {...props}>
      {children}
    </p>
  )
}
