import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TextField } from '../../components/ui/TextField'

describe('TextField', () => {
  it('associates the label with the input', () => {
    render(<TextField label="Assistant name" value="Chintu" onChange={() => {}} />)

    expect(screen.getByLabelText('Assistant name')).toHaveValue('Chintu')
  })

  it('renders an optional description', () => {
    render(
      <TextField
        label="Assistant name"
        description="Shown throughout the app."
        value=""
        onChange={() => {}}
      />,
    )

    expect(screen.getByText('Shown throughout the app.')).toBeInTheDocument()
  })

  it('calls onChange as the user types', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<TextField label="Assistant name" value="" onChange={onChange} />)

    await user.type(screen.getByLabelText('Assistant name'), 'C')

    expect(onChange).toHaveBeenCalled()
  })

  it('renders an error message and marks the input invalid', () => {
    render(
      <TextField label="Assistant name" value="" onChange={() => {}} error="must not be blank" />,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('must not be blank')
    expect(screen.getByLabelText('Assistant name')).toHaveAttribute('aria-invalid', 'true')
  })

  it('has a visible keyboard focus ring, like every other interactive control', () => {
    render(<TextField label="Assistant name" value="" onChange={() => {}} />)

    expect(screen.getByLabelText('Assistant name')).toHaveClass('focus-visible:ring-2')
  })
})
