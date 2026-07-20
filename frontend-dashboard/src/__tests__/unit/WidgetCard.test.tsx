import { render, screen } from '@testing-library/react'
import { Bell } from 'lucide-react'
import { describe, expect, it } from 'vitest'
import { WidgetCard } from '../../components/dashboard/WidgetCard'

describe('WidgetCard', () => {
  it('renders the title as a heading and the children as content', () => {
    render(
      <WidgetCard title="Reminders">
        <p>3 upcoming</p>
      </WidgetCard>,
    )

    expect(screen.getByRole('heading', { level: 2, name: 'Reminders' })).toBeInTheDocument()
    expect(screen.getByText('3 upcoming')).toBeInTheDocument()
  })

  it('renders an optional icon decoratively, not announced by itself', () => {
    render(
      <WidgetCard icon={Bell} title="Reminders">
        content
      </WidgetCard>,
    )

    const heading = screen.getByRole('heading', { level: 2, name: 'Reminders' })
    // The icon sits next to the heading but carries aria-hidden, so it isn't
    // a second accessible name for anything.
    expect(heading.parentElement?.querySelector('svg')).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders without an icon when none is given', () => {
    render(<WidgetCard title="Reminders">content</WidgetCard>)

    expect(
      screen
        .getByRole('heading', { level: 2, name: 'Reminders' })
        .parentElement?.querySelector('svg'),
    ).toBeNull()
  })
})
