import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { HealthStatus } from '../../components/HealthStatus'
import type { HealthState } from '../../api/useHealth'

describe('HealthStatus', () => {
  it('shows a loading message', () => {
    render(<HealthStatus health={{ kind: 'loading' }} />)

    expect(screen.getByRole('status')).toHaveTextContent('Checking backend health')
  })

  it('shows the app name, status, and environment on success', () => {
    const health: HealthState = {
      kind: 'success',
      data: { status: 'ok', app_name: 'Jarvis', environment: 'staging' },
    }

    render(<HealthStatus health={health} />)

    expect(screen.getByRole('status')).toHaveTextContent('Jarvis backend is ok (staging)')
  })

  it('shows an error message when the backend is unreachable', () => {
    render(<HealthStatus health={{ kind: 'error' }} />)

    expect(screen.getByRole('alert')).toHaveTextContent('Could not reach the backend')
  })
})
