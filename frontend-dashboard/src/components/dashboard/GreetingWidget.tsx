import { useEffect, useState } from 'react'
import { Heading } from '../ui/Heading'
import { Text } from '../ui/Text'
import { getGreeting } from './greeting'

// A minute is plenty of precision for a greeting bucket (morning/afternoon/
// evening/night) — unlike ClockWidget, this doesn't need second-by-second
// updates, just to notice when the bucket changes while the page stays open
// (e.g. an always-on Smart Display).
const REFRESH_INTERVAL_MS = 60_000

export function GreetingWidget({ appName }: { appName: string }) {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), REFRESH_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  return (
    <div>
      <Heading level={1}>{getGreeting(now)}</Heading>
      <Text variant="muted" className="mt-1">
        {appName} is ready to help.
      </Text>
    </div>
  )
}
