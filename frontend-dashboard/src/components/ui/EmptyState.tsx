import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import { Heading } from './Heading'
import { Text } from './Text'

export interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 px-6 py-16 text-center">
      <Icon aria-hidden="true" className="h-10 w-10 text-slate-400 dark:text-slate-500" />
      <Heading level={2}>{title}</Heading>
      {description && <Text variant="muted">{description}</Text>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
