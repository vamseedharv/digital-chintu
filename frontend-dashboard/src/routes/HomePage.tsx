import { useOutletContext } from 'react-router'
import type { AppShellContext } from '../app/AppShell'
import { HealthStatus } from '../components/HealthStatus'
import { Heading } from '../components/ui/Heading'

export function HomePage() {
  const { health } = useOutletContext<AppShellContext>()

  return (
    <div className="space-y-6">
      <Heading level={1}>System status</Heading>
      <HealthStatus health={health} />
    </div>
  )
}
