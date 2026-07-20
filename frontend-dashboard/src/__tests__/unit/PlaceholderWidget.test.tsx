import { render, screen } from '@testing-library/react'
import { CloudSun } from 'lucide-react'
import { describe, expect, it } from 'vitest'
import { PlaceholderWidget } from '../../components/dashboard/PlaceholderWidget'

describe('PlaceholderWidget', () => {
  it('renders the title, description, and a "coming soon" marker', () => {
    render(
      <PlaceholderWidget icon={CloudSun} title="Weather" description="Local weather forecast." />,
    )

    expect(screen.getByRole('heading', { level: 2, name: 'Weather' })).toBeInTheDocument()
    expect(screen.getByText('Local weather forecast.')).toBeInTheDocument()
    expect(screen.getByText('Coming soon')).toBeInTheDocument()
  })
})
