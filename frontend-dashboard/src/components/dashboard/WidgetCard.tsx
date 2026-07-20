import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import { Card } from '../ui/Card'
import { Heading } from '../ui/Heading'

export interface WidgetCardProps {
  icon?: LucideIcon
  title: string
  children: ReactNode
}

// Shared Card + icon + <h2> shell so a new widget only has to write its own
// content, not re-derive this layout — every widget tile (built-in or a
// future feature's) renders through this one component.
export function WidgetCard({ icon: Icon, title, children }: WidgetCardProps) {
  return (
    <Card>
      <div className="flex items-center gap-2">
        {Icon && <Icon aria-hidden="true" className="h-5 w-5 text-brand-600 dark:text-brand-400" />}
        <Heading level={2}>{title}</Heading>
      </div>
      <div className="mt-3">{children}</div>
    </Card>
  )
}
