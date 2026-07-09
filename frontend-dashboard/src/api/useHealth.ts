import { useEffect, useState } from 'react'
import { fetchHealth, type HealthResponse } from './health'

export type HealthState =
  { kind: 'loading' } | { kind: 'success'; data: HealthResponse } | { kind: 'error' }

export function useHealth(): HealthState {
  const [status, setStatus] = useState<HealthState>({ kind: 'loading' })

  useEffect(() => {
    let cancelled = false

    fetchHealth()
      .then((data) => {
        if (!cancelled) setStatus({ kind: 'success', data })
      })
      .catch(() => {
        if (!cancelled) setStatus({ kind: 'error' })
      })

    return () => {
      cancelled = true
    }
  }, [])

  return status
}
