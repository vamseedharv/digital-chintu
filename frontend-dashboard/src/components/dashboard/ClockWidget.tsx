import { useEffect, useState } from 'react'
import { Clock } from 'lucide-react'
import { Text } from '../ui/Text'
import { WidgetCard } from './WidgetCard'

const REFRESH_INTERVAL_MS = 1_000

export function ClockWidget() {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), REFRESH_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  return (
    <WidgetCard icon={Clock} title="Clock">
      {/* Not an aria-live region on purpose — a ticking clock announcing
          itself every second would be noise for screen reader users; the
          time is available on request, same as any other static text. */}
      <p className="text-3xl font-semibold tabular-nums text-slate-900 dark:text-slate-50">
        {now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
      </p>
      <Text variant="muted" className="mt-1">
        {now.toLocaleDateString([], {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })}
      </Text>
    </WidgetCard>
  )
}
