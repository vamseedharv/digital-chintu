import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { SelectField } from '../../components/ui/SelectField'

const OPTIONS = [
  { value: 'system', label: 'Match system' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
]

describe('SelectField', () => {
  it('associates the label with the select and lists every option', () => {
    render(<SelectField label="Theme" options={OPTIONS} value="system" onChange={() => {}} />)

    const select = screen.getByLabelText('Theme')
    expect(select).toHaveValue('system')
    expect(screen.getByRole('option', { name: 'Light' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Dark' })).toBeInTheDocument()
  })

  it('renders an optional description', () => {
    render(
      <SelectField
        label="Theme"
        description="The default before a browser chooses its own."
        options={OPTIONS}
        value="system"
        onChange={() => {}}
      />,
    )

    expect(screen.getByText('The default before a browser chooses its own.')).toBeInTheDocument()
  })

  it('calls onChange when a different option is selected', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<SelectField label="Theme" options={OPTIONS} value="system" onChange={onChange} />)

    await user.selectOptions(screen.getByLabelText('Theme'), 'dark')

    expect(onChange).toHaveBeenCalled()
  })

  it('has a visible keyboard focus ring, like every other interactive control', () => {
    render(<SelectField label="Theme" options={OPTIONS} value="system" onChange={() => {}} />)

    expect(screen.getByLabelText('Theme')).toHaveClass('focus-visible:ring-2')
  })
})
