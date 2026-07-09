import clsx from 'clsx'
import type { HTMLAttributes } from 'react'
import { createElement } from 'react'

export interface HeadingProps extends HTMLAttributes<HTMLHeadingElement> {
  level?: 1 | 2 | 3 | 4
}

const LEVEL_CLASSES: Record<1 | 2 | 3 | 4, string> = {
  1: 'text-2xl font-semibold tracking-tight',
  2: 'text-lg font-semibold',
  3: 'text-base font-semibold',
  4: 'text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400',
}

export function Heading({ level = 1, className, children, ...props }: HeadingProps) {
  return createElement(
    `h${level}`,
    { className: clsx(LEVEL_CLASSES[level], className), ...props },
    children,
  )
}
