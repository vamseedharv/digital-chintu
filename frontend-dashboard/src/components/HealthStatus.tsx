import type { HealthState } from '../api/useHealth'
import { Card } from './ui/Card'
import { Heading } from './ui/Heading'
import { Skeleton } from './ui/Skeleton'

export function HealthStatus({ health }: { health: HealthState }) {
  return (
    <Card>
      <Heading level={2}>Backend connection</Heading>

      {health.kind === 'loading' && (
        <div className="mt-3" role="status">
          <span className="sr-only">Checking backend health…</span>
          <Skeleton className="h-4 w-48" />
        </div>
      )}

      {health.kind === 'success' && (
        <p className="mt-2 text-emerald-600 dark:text-emerald-400" role="status">
          {health.data.app_name} backend is {health.data.status} ({health.data.environment})
        </p>
      )}

      {health.kind === 'error' && (
        <p className="mt-2 text-red-600 dark:text-red-400" role="alert">
          Could not reach the backend. Is it running?
        </p>
      )}
    </Card>
  )
}
