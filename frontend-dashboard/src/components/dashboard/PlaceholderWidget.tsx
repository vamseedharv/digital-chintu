import type { LucideIcon } from 'lucide-react'
import { Text } from '../ui/Text'
import { WidgetCard } from './WidgetCard'

export interface PlaceholderWidgetProps {
  icon: LucideIcon
  title: string
  description: string
}

// Generic "not built yet" tile for a widget whose real feature hasn't
// landed — reused for Weather/Reminders/To-do/Shopping list today. Once one
// of those features exists, its own real widget replaces this call site;
// this component itself doesn't need to change.
export function PlaceholderWidget({ icon, title, description }: PlaceholderWidgetProps) {
  return (
    <WidgetCard icon={icon} title={title}>
      <Text variant="muted">{description}</Text>
      <Text
        variant="caption"
        className="mt-3 font-medium uppercase tracking-wide text-brand-600 dark:text-brand-400"
      >
        Coming soon
      </Text>
    </WidgetCard>
  )
}
