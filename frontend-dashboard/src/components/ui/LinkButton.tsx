import { Link } from 'react-router'
import type { ComponentProps } from 'react'
import { buttonClasses } from './buttonStyles'
import type { ButtonSize, ButtonVariant } from './buttonStyles'

export interface LinkButtonProps extends ComponentProps<typeof Link> {
  variant?: ButtonVariant
  size?: ButtonSize
}

/** A react-router Link styled like Button — for navigation actions (e.g. an
 * EmptyState's "Back to Home") that must be a real link, not a <button>. */
export function LinkButton({
  variant = 'primary',
  size = 'md',
  className,
  ...props
}: LinkButtonProps) {
  return <Link className={buttonClasses({ variant, size, className })} {...props} />
}
